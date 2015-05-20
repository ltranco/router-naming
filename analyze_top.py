# CSE 199H - Router Naming
# Student: Long Tran | lt@ucsd.edu
# Supervisors: kc, Bradley Huffaker, Matthew Luckie
# File: 
# Purpose: 

#import re
import sqlite3 as lite
import sys
import operator

def top(cur):
	hostname_freq_map = {}
	cur.execute("SELECT DISTINCT NodeDegree.NodeId, NodeHost.PublicSuffix, NodeDegree.HostNameDegree"
			+" FROM NodeDegree"
			+" JOIN NodeHost ON NodeDegree.NodeId = NodeHost.NodeId"
			+" WHERE HostNameDegree > 2"
				+" AND HostNameDegree < 10"
			+" ORDER BY NodeDegree.NodeId"
			+";")
	rows = cur.fetchall()

	for row in rows:										# Process data to find frequency of each hostname
		hostname = row[1]
		if hostname in hostname_freq_map:
			hostname_freq_map[hostname] = hostname_freq_map[hostname] + 1
		else:
			hostname_freq_map[hostname] = 1

	sorted_hostname_freq_map = sorted(hostname_freq_map.items(), key=operator.itemgetter(1), reverse=True)
	l = [k for k in hostname_freq_map if hostname_freq_map[k] > 150]
	print len(l)	
	print len(sorted_hostname_freq_map)

def main():
	try:
		con = lite.connect('../../../router-naming.db')			# Connecting to db
		cur = con.cursor()
		top(cur)
		con.commit()

	except lite.Error, e:
		if con:
			con.rollback()
		print "Database error %s:" % e.args[0]
		sys.exit(1)

	finally:
	    if con:
	        con.close()

main()

#(u'level3.net', 856), (u'comcast.net', 789), (u'rr.com', 580), (u'telia.net', 557), (u'cogentco.com', 427), (u'virginmedia.net', 409), (u'tinet.net', 409), (u'ntt.net', 402), (u'alter.net', 362), (u'gblx.net', 305), (u'yahoo.com', 261), (u'163data.com.cn', 252), (u'sbcglobal.net', 247), (u'windstream.net', 224), (u'sfr.net', 198), (u'pccwbtn.net', 197), (u'zz.ha.cn', 189), (u'kddi.ne.jp', 186), (u'above.net', 184), (u'dtag.de', 173), (u'seabone.net', 171), (u'adsl', 171), (u'hetzner.de', 168), (u'xo.net', 165), (u'vsnl.net.in', 163), (u'savvis.net', 152), (u'as6453.net', 140), (u'as9143.net', 139), (u'suddenlink.net', 135), (u'adsl-pool.sx.cn', 133), (u'bhn.net', 132), (u'sprintlink.net', 126), (u'telenor.net', 125), (u'embratel.net.br', 125), (u'as2116.net', 124), (u'hinet.net', 121), (u'he.net', 113), (u'asianetcom.net', 111), (u'nlayer.net', 110), (u'telemar.net.br', 108), (u'qwest.net', 102),






