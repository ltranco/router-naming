import re
import sys

def main():
	if len(sys.argv) != 2:
		print "Usage: python analyze_regex.py <data_file>"
		sys.exit(1)
	read_file = open(sys.argv[1], 'r')
	data_file = read_file.readlines()
	dicts = get_router_id(data_file, str(sys.argv[1]))
	validate(dicts[0], dicts[1], dicts[2], dicts[3])

def get_router_id(data_file, host):
	rid_nid = {}
	nid_rid = {}
	nid_host_count = {}			# Count how many hostnames for each NodeID in original file
	nid_host_count_re = {}		# Count how many hostnames for each NodeId found using supposed regex

	for data in data_file:
		router_id, hostname, router_id, node_id = "", "", "", ""
		
		# Count how many hostnames each NodeId is supposed to have
		match = re.match("(N\d+)", data)
		if match:
			node_id = match.group(1)
			if node_id in nid_host_count:
				nid_host_count[node_id] = nid_host_count[node_id] + 1
			else:
				nid_host_count[node_id] = 1

		if host == "alter.txt":									#93.08
			match = re.match("N(\d+)\s*(\w*.?)([-\w]*)\.([-\w]*)\.(\w*)\.alter.net", data)
			if match:
				router_id = (match.group(4), match.group(5))
				node_id = "N" + match.group(1)
				hostname = re.search("(\w*.?)([-\w]*)\.([-\w]*)\.(\w*)\.alter.net", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "yahoo.txt":									#84.92 What to do with unknowns?%
			match = re.match("N(\d+)\s*[-\w]*\.([-\w]*)\.(\w*)\.yahoo\.com", data)
			if match:
				router_id = (match.group(2), match.group(3))
				node_id = "N" + match.group(1)
				hostname = re.search("[-\w]*\.([-\w]*)\.(\w*)\.yahoo\.com", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "rr.txt":									#77%
			match = re.match("N(\d+)\s*[-\w]*\.([-\w]*)\.(\w*)\.(tbone.)?rr\.com", data)
			if match:
				router_id = (match.group(2), match.group(3))
				node_id = "N" + match.group(1)
				hostname = re.search("[-\w]*\.([-\w]*)\.(\w*)\.(tbone.)?rr\.com", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "cogentco.txt":								#96.52%
			match = re.match("N(\d+)\s*[-\w.]*\.(\w*)\.(\w*)\.atlas\.cogentco\.com", data)
			if match:
				router_id = (match.group(2), match.group(3))
				node_id = "N" + match.group(1)
				hostname = re.search("[-\w]*\.(\w*)\.(\w*)\.atlas\.cogentco\.com", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "comcast.txt":								#93.30%
			match = re.match("N(\d+)\s*[\w-]*(\w{3}\d\d)\.(\w*)\.(\w*)\.(\w*)\.comcast\.net", data)
			if match:
				router_id = (match.group(2), match.group(3), match.group(4), match.group(5))
				node_id = "N" + match.group(1)
				hostname = re.search("[\w-]*(\w{3}\d\d)\.(\w*)\.(\w*)\.(\w*)\.comcast\.net", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "telia.txt":									#86.30%
			match = re.match("N(\d+)\s*(\w*)-(\w*)-(\w*)-(\w*)-(\w*)\.c.telia.net", data)
			if match:
				#router_id = (match.group(2), match.group(3), match.group(5), match.group(6))
				router_id = (match.group(2), match.group(5), match.group(6)) #86.30
				#router_id = (match.group(2), match.group(5)) #85
				node_id = "N" + match.group(1)
				hostname = re.search("(\w*)-(\w*)-(\w*)-(\w*)-(\w*)\.c.telia.net", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "virginmedia.txt":							#99.47%
			match = re.match("N(\d+)\s*(\w*)-(\w*)-(\w*)([-\w])*\.network\.virginmedia\.net", data)
			if match:
				router_id = (match.group(2), match.group(3), match.group(4))
				node_id = "N" + match.group(1)
				hostname = re.search("(\w*)-(\w*)-(\w*)([-\w])*\.network\.virginmedia\.net", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "tinet.txt":
			match = re.match("N(\d+)\s*(\w*)-(\w*)-(\w*)-(\w*)\.(\w*)\.(\w*)\.tinet.net", data)
			if match:
				router_id = (match.group(2), match.group(6))	#BAD DATA PROBABLY
				node_id = "N" + match.group(1)
				hostname = re.search("([\w-]*)\.(\w*)\.(\w*)\.tinet.net", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if host == "ntt.txt":
			match = re.match("N(\d+)\s*([\w-]*)\.(\w*)\.(\w*)\.(\w*)\.(\w*)\.(\w*)\.ntt.net", data)
			if match:
				router_id = (match.group(4), match.group(5), match.group(7))   #88.76
				node_id = "N" + match.group(1)
				hostname = re.search("([\w-]*)\.(\w*)\.(\w*)\.(\w*)\.(\w*)\.(\w*)\.ntt.net", data).group(0)
				if node_id in nid_host_count_re:
					nid_host_count_re[node_id] = nid_host_count_re[node_id] + 1
				else:
					nid_host_count_re[node_id] = 1

		if router_id in rid_nid:
			if router_id != "":
				rid_nid[router_id][node_id] = hostname
		else:
			if router_id != "":
				rid_nid[router_id] = {node_id : hostname}

		if node_id in nid_rid:
			if router_id != "":
				nid_rid[node_id][router_id] = hostname
		else:
			if router_id != "":	
				nid_rid[node_id] = {router_id : hostname}
	return (rid_nid, nid_rid, nid_host_count, nid_host_count_re)

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
            print key
            print rid_nid[key]
            print "\n"

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

main()