import re
import itertools
import operator
import sqlite3 as lite

def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and is_substr(data[0][i:i+j], data):
                    substr = data[0][i:i+j]
    return substr

def is_substr(find, data):
    if len(data) < 1 and len(find) < 1:
        return False
    for i in range(len(data)):
        if find not in data[i]:
            return False
    return True

def get_data(db_path, domain):
    try:
        con = lite.connect(db_path)
        cur = con.cursor()

        cur.execute("SELECT DISTINCT NodeDegree.NodeId, NodeHost.HostName, NodeDegree.HostNameDegree"
            +" FROM NodeHost"
            +" JOIN NodeDegree ON NodeDegree.NodeId = NodeHost.NodeId"
            +" WHERE HostNameDegree > 2"
                +" AND HostNameDegree < 10"
                +" AND PublicSuffix = \"" + domain + "\""
            +" ORDER BY NodeDegree.NID"
            +";")
        return cur.fetchall()
    except lite.Error, e:
        if con:
            con.rollback()
        print "Database error %s:" % e.args[0]
        sys.exit(1)
    finally:
        if con: 
            con.close()

def get_routers(data):
    d = {}
    for row in data:
        if row[0] in d: d[row[0]].append(row[1])
        else: d[row[0]] = [row[1]]

    #remove those with 1 or less hostname
    #new_d = {k:d[k] for k in d if len(d[k]) > 1}
    #printDict(new_d)
    return d

def cut_string(dic, cut):
    return {k:[h.replace(cut, '') for h in dic[k]] for k in dic}

def lcs_per_router(l, threshold):
    longest = ''
    for perm in list(itertools.permutations(l, threshold)):
        s = long_substr(perm)
        if len(s) > len(longest): longest = s
    return longest

def pseudo_regex(s):
    l = re.split("[a-z\d]+", s)
    #print len(l)
    return "([a-z\d]+)".join(l)

def collect_regex_result1(datasrc, regex):
    #datasrc is a dictionary mapping nid : [list of associated hostnames]
    rid_nid = {}
    nid_rid = {}

    # Count how many hostnames for each NodeID in original data source
    nid_host = {k : len(datasrc[k]) for k in datasrc}         

    nid_host_re = {}      # Count how many hostnames for each NodeId found using supposed regex

    for nid in datasrc:
        for hn in datasrc[nid]:
            match = re.match(regex, hn)
            if match:
                #print hn + " matched"
                nid_host_re[nid] = nid_host_re.get(nid, 0) + 1
                rid = match.group(0)
                if rid != "":
                    if rid in rid_nid: 
                        if nid in rid_nid[rid]: rid_nid[rid][nid].append(hn)
                        else: rid_nid[rid] = {nid: [hn]}
                    else: rid_nid[rid] = {nid : [hn]}
                if nid in nid_rid: 
                    if rid in nid_rid[nid]: nid_rid[nid][rid].append(hn)
                    else: nid_rid[nid] = {rid : [hn]}
                else: nid_rid[nid] = {rid : [hn]}
            #else:
                #print hn + " not match"
        #print "\n"
    return (rid_nid, nid_rid, nid_host, nid_host_re)

def try_group(groups):
    return list(itertools.combinations(range(1, groups + 1), 2)) + list(itertools.combinations(range(1, groups + 1), 3))

def collect_regex_result(datasrc, regex, group):
    
    
    #datasrc is a dictionary mapping nid : [list of associated hostnames]
    rid_nid = {}
    nid_rid = {}

    # Count how many hostnames for each NodeID in original data source
    nid_host = {k : len(datasrc[k]) for k in datasrc}         

    nid_host_re = {}      # Count how many hostnames for each NodeId found using supposed regex

    for nid in datasrc:
        for hn in datasrc[nid]:
            match = re.match(regex, hn)
            if match:
                #print hn + " matched"
                nid_host_re[nid] = nid_host_re.get(nid, 0) + 1
                rid = tuple([match.group(g) for g in group])

                if rid:
                    if rid in rid_nid: 
                        if nid in rid_nid[rid]: rid_nid[rid][nid].append(hn)
                        else: rid_nid[rid][nid] = [hn]
                    else: rid_nid[rid] = {nid : [hn]}

                if nid in nid_rid: 
                    if rid in nid_rid[nid]: nid_rid[nid][rid].append(hn)
                    else: nid_rid[nid][rid] = [hn]
                else: nid_rid[nid] = {rid : [hn]}
            #else:
                #print hn + " not match"
        #print "\n"
    return (rid_nid, nid_rid, nid_host, nid_host_re)

def printDict(d):
    for k in d: print "%s\t\t%s" % (k, d[k])

def validate(rid_nid, nid_rid, nid_host_count, nid_host_count_re):
    # Verifying dictionaries; should have 1-1 mapping
    # #node id perfect, #nodeids missed completely, #nodeids mixed, #nodeids partial
    perfect = 0
    missed = 0
    split = 0
    partial = 0
    no_router = 0
    mixed = 0

    for key in rid_nid:
        if len(rid_nid[key]) == 0:
            no_router += 1
        elif len(rid_nid[key]) > 1:
            mixed += 1
            #print key
            #print rid_nid[key]
            #print "\n"

    for key in nid_rid:
        if len(nid_rid[key]) == 0:
            missed += 1
        elif len(nid_rid[key]) > 1:
            split += 1
            #print key
            #print nid_rid[key]
            #print "\n\n"
            
        elif len(nid_rid[key]) == 1:
            check_rid = nid_rid[key].keys()[0]
            
            if check_rid in rid_nid:
                if key in nid_host_count and key in nid_host_count_re and len(rid_nid[check_rid]) == 1 and key == rid_nid[check_rid].keys()[0]:
                    if nid_host_count[key] == nid_host_count_re[key]:
                        perfect += 1
                        #print key + " is perfect"
                    else:
                        partial += 1
                        #print "should get %d" % nid_host_count[key]
                        #print "only found %d" % nid_host_count_re[key]
                        #print key
                        #print nid_rid[key]
                        #print "\n"
    
    acc = perfect * 100.0/len(nid_host_count)
    print "# Perfect\t# Missed\t# Split\t\t# Mixed\t\t# Partial\t# No Router\tAccuracy"              
    print "%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t%.2f" % (perfect, missed, split, mixed, partial, no_router, acc)
    
    printDict(rid_nid)
    printDict(nid_rid)

    #print len(nid_host_count)
    #print len(nid_host_count_re)
    #print "\n\n"
    return acc

def sanitize_lcs(lcs):
    return [m.group(1) if m else n for n in lcs for m in [re.match("^.*?\.(.*)", n)]]

def main1():
    data = get_data('../../../router-naming.db', 'cogentco.com')
    d = get_routers(data)
    d = cut_string(d, 'cogentco.com')
    
    max_acc = 0.0
    best_group = ()
    best_re = ""
    size = 0

    curr_lcs = [lcs_per_router(d[nid], 2) for nid in d]
    curr_lcs = set(sanitize_lcs(curr_lcs))
    for i in curr_lcs: print i
    try_regex = set([pseudo_regex(c) for c in curr_lcs if c != ""])

    #print curr_lcs

    for t in try_regex:
        groups = try_group(re.compile(t).groups)
        print t
        #print groups
        for group in groups:
            r = collect_regex_result(d, t, group)
            print group
            m = validate(r[0], r[1], r[2], r[3])
            if m > max_acc: 
                max_acc = m
                best_group = group
                best_re = t
                size = len(r[2])
            #print "\n"

    print "%d %f %s %s" % (size, max_acc, best_re, best_group)

def main3():
    print "main3"
    data = get_data('../../../router-naming.db', 'cogentco.com')
    d = get_routers(data)
    d = cut_string(d, 'cogentco.com')

    curr_lcs = [lcs_per_router(d[nid], 2) for nid in d]
    curr_lcs = set(sanitize_lcs(curr_lcs))
    
    
    try_regex = [pseudo_regex("mag21.ams03.atlas.")]
    try_regex = "([a-z\d]+).([a-z\d]+)..*.cogentco.com$"
    try_regex = "([a-z\d]+).([a-z\d]+)\.[a-z\d]+\.cogentco.com$"
    hosts = d["N1647"]
    for h in hosts:
        print h
        print re.findall(try_regex, h+"cogentco.com")
    #N1647           be2440.mag21.ams03.atlas.cogentco.com 
    #N1647           be3356.mag21.ams03.atlas.cogentco.com
    #N1647           te0-0-0-22.mag21.ams03.atlas.cogentco.com
    #N1647           te0-0-0-3.mag21.ams03.atlas.cogentco.com
    #N1647           te0-7-0-17.mag21.ams03.atlas.cogentco.com
    #N1647           te0-7-0-3.mag21.ams03.atlas.cogentco.com



main3()































