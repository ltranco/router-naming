import re
import itertools
import operator
import sqlite3 as lite
import sys

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
    
def top(db_path):
    try:
        con = lite.connect(db_path)         # Connecting to db
        cur = con.cursor()
        hostname_freq_map = {}
        cur.execute("SELECT DISTINCT NodeDegree.NodeId, NodeHost.PublicSuffix, NodeDegree.HostNameDegree"
                +" FROM NodeDegree"
                +" JOIN NodeHost ON NodeDegree.NodeId = NodeHost.NodeId"
                +" WHERE HostNameDegree > 2"
                    +" AND HostNameDegree < 10"
                +" ORDER BY NodeDegree.NodeId"
                +";")
        rows = cur.fetchall()

        for row in rows:                                        # Process data to find frequency of each hostname
            hostname = row[1]
            if hostname in hostname_freq_map:
                hostname_freq_map[hostname] = hostname_freq_map[hostname] + 1
            else:
                hostname_freq_map[hostname] = 1

        sorted_hostname_freq_map = sorted(hostname_freq_map.items(), key=operator.itemgetter(1), reverse=True)
        l = [k for k in hostname_freq_map if hostname_freq_map[k] > 150]    
        print len(sorted_hostname_freq_map)
    except lite.Error, e:
        if con:
            con.rollback()
        print "Database error %s:" % e.args[0]
        sys.exit(1)
    finally:
        if con:
            con.close()

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
    return {k:d[k] for k in d if len(d[k]) > 1}

def cut_string(dic, cut):
    return {k:[h.replace(cut, '') for h in dic[k]] for k in dic}

def lcs_per_router(l, threshold):
    longest = ''
    for perm in list(itertools.permutations(l, threshold)):
        s = long_substr(perm)
        if len(s) > len(longest): longest = s
    return longest

def pseudo_regex(s, perm_flag):
    r = []
    l1 = re.split("[a-z\d]+", s)
    l1 = ["\." if i == "." else i for i in l1]
    if perm_flag:
        total_groups = len(l1) - 1
        for g_combo in try_group(total_groups):                 #for each tuple of possible groups combination
            l2 = ["([a-z\d]+)" if i in g_combo else "[a-z\d]+" for i in xrange(1, total_groups + 1)]
            r.append("".join(cross_two_lists(l1, l2)))
        return r
    else:
        return "[a-z\d]+".join(l1)

def cross_two_lists(l1, l2):
    return list(i.next() for i in itertools.cycle([iter(l1), iter(l2)]))

def collect_regex_result(datasrc, regex, domain):
    #datasrc is a dictionary mapping nid : [list of associated hostnames]
    rid_nid = {}
    nid_rid = {}

    # Count how many hostnames for each NodeID in original data source
    nid_host = {k : len(datasrc[k]) for k in datasrc}         

    nid_host_re = {}      # Count how many hostnames for each NodeId found using supposed regex

    for nid in datasrc:
        for hn in datasrc[nid]:
            match = re.findall(regex, hn + domain)
            if match:
                nid_host_re[nid] = nid_host_re.get(nid, 0) + 1
                rid = tuple([s for tup in match for s in tup])

                if rid:
                    if rid in rid_nid: 
                        if nid in rid_nid[rid]: rid_nid[rid][nid].append(hn)
                        else: rid_nid[rid][nid] = [hn]
                    else: rid_nid[rid] = {nid : [hn]}

                if nid in nid_rid: 
                    if rid in nid_rid[nid]: nid_rid[nid][rid].append(hn)
                    else: nid_rid[nid][rid] = [hn]
                else: nid_rid[nid] = {rid : [hn]}
    return (rid_nid, nid_rid, nid_host, nid_host_re)

def try_group(groups):
    return list(itertools.combinations(range(1, groups + 1), 2)) + list(itertools.combinations(range(1, groups + 1), 3))

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

    for key in nid_rid:
        if len(nid_rid[key]) == 0:
            missed += 1
        elif len(nid_rid[key]) > 1:
            split += 1
            
        elif len(nid_rid[key]) == 1:
            check_rid = nid_rid[key].keys()[0]
            
            if check_rid in rid_nid:
                if key in nid_host_count and key in nid_host_count_re and len(rid_nid[check_rid]) == 1 and key == rid_nid[check_rid].keys()[0]:
                    if nid_host_count[key] == nid_host_count_re[key]:
                        perfect += 1
                    else:
                        partial += 1
    
    acc = perfect * 100.0/len(nid_host_count)
    if acc >= 0:
        print "# Perfect\t# Missed\t# Split\t\t# Mixed\t\t# Partial\t# No Router\tAccuracy"              
        print "%d\t\t\t%d\t\t\t%d\t\t\t%d\t\t\t%d\t\t\t%d\t\t\t%.2f" % (perfect, missed, split, mixed, partial, no_router, acc)
    
    return acc

def sanitize_lcs(lcs):
    return [m.group(1) if m else n for n in lcs for m in [re.match("^.*?\.(.*)", n)]]

def is_digit(n):
    try: return isinstance(int(n), int)
    except ValueError: return False

def re_left_over(left_over):
    return set(["([^\.]+\.){%d}" % (len(re.split("\.", l)) - 1) for l in left_over]) if len(left_over) > 0 else ""

def find_left_over(hostnames, lcs):
    return [l for l in [h[h.rfind(lcs) + len(lcs):] for h in hostnames] if l != ""]

def combine_re(head, tail):
    return [h + t for h in head for t in tail]

def flatten_list(list_of_list):
    return [item for sub_list in list_of_list for item in sub_list]

def output_best_re(d, best_re):
    for k in d:
        for h in d[k]:
            print ("%s\t%s" % (k, h)).ljust(50),
            print "\t\t%s" % (" ".join(tuple([s for tup in re.findall(best_re, h) for s in tup])))
        print

def main():
    #domains = ["comcast.net", "rr.com", "telia.net", "cogentco.com", "virginmedia.net", "ntt.net", "alter.net", "yahoo.com"]
    domains = ["telia.net"]
    for domain in domains:
        data = get_data('../../../router-naming.db', domain)
        d = get_routers(data)
        d = cut_string(d, domain)

        max_acc = 0.0
        best_re = ""
        size = 0

        try_regex = []

        for nid in d:
            lcs = long_substr(d[nid])
            left_over = find_left_over(d[nid], lcs)
            try_regex.append(combine_re(pseudo_regex(lcs, True), re_left_over(left_over)))
        
        try_regex = set(flatten_list(try_regex))
        
        for t in try_regex:
            t += domain + "$"
            r = collect_regex_result(d, t, domain)
            m = validate(r[0], r[1], r[2], r[3])
            if m > max_acc: 
                max_acc = m
                best_re = t
                size = len(r[2])  
            if m >= 0:
                print t
                print "\n\n"
            
        print "%d %f %s" % (size, max_acc, best_re)

main()