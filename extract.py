# CSE 199H - Router Naming
# Student: Long Tran | lt@ucsd.edu
# Supervisors: kc, Bradley Huffaker, Matthew Luckie
# File: extract.py
# Purpose: This file extracts information from midar-run-20140421-dns-names.txt and midar-iff.nodes and put them into router-naming.db

import re
import sqlite3 as lite
import sys
from publicsuffix import PublicSuffixList

def extract_host():
	host_file = open('data_set/midar-run-20140421-dns-names.txt', 'r')	# Read in host file (midar-run-20140421-dns-names.txt)
	host_file_data = host_file.readlines()
	ip_hostname_map = {}

	for each_line in host_file_data:
		split_line = each_line.split()									# <timestamp> <ip> <hostname>
		
		if len(split_line) >= 3:										# If all components present	
			hostname = split_line[2]							
			if not hostname[0].isupper():								# Check hostname for no uppercase letter
				ip = split_line[1]
				ip_hostname_map[ip] = hostname
				
	return ip_hostname_map

def main():
	ip_hostname_map = extract_host()									# Get ip::hostname map
	
	try:
		con = lite.connect('router-naming.db')							# Connecting to db
		cur = con.cursor()

		#cur.execute("DROP TABLE IF EXISTS NodeHost")					# Creating tables
		#cur.execute("DROP TABLE IF EXISTS NodeDegree")
		cur.execute("CREATE TABLE NodeHost(IP TEXT, PublicSuffix TEXT, HostName TEXT, NodeID TEXT, NID INT)")
		cur.execute("CREATE TABLE NodeDegree(IpDegree INT, HostNameDegree INT, NodeID TEXT, NID INT)")

		p = PublicSuffixList()											# Stripping public suffix domain

		node_file = open('data_set/midar-iff.nodes', 'r')				# Read in node file (midar-iff.nodes)
		node_file_data = node_file.readlines()

		for row in node_file_data:										# Go through all nodes
			if row[0] != "#":											# Ignore comments
				
				node_id = re.search(r'N\d*', row).group()				# Find node id in form of N<digits>
				node_id_int = node_id[1:]

				match_ip = re.split(r'node\sN\d*:\s*', row)				# Find list of ip addr of this node
				ip_list = match_ip[1].split()

				hit_count = 0											# Count ips found in ip::hostname map

				for ip in ip_list:										# Check all ips of this node
					if ip in ip_hostname_map:
						hit_count += 1
						hostname = ip_hostname_map[ip]
						public_sfx = p.get_public_suffix(hostname)
						cur.execute(r"INSERT INTO NodeHost VALUES('%s', '%s', '%s', '%s', '%s');" % (ip, public_sfx, hostname, node_id, node_id_int))

				if hit_count > 0:										# If there is at least one hit
					cur.execute(r"INSERT INTO NodeDegree VALUES(%d, %d, '%s', '%s');" % (len(ip_list), hit_count, node_id, node_id_int))
		con.commit()

	except lite.Error, e:
		if con:
			con.rollback()
		print "Databse error %s:" % e.args[0]
		sys.exit(1)

	finally:
	    if con:
	        con.close()

main()