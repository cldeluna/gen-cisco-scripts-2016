#!/usr/bin/python -tt
# get_vlans.py
# Claudia
# PyCharm
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "7/3/15  9:54 AM"
__copyright__ = "Copyright (c) 2015 Claudia de Luna"
__license__ = "Python"

import sys
import re
import os



# Provided main() calls the above functions

# Provided main() calls the above functions
def main():
    # Take path argument and list all text files
    """
    Description
    :return:
    """



    path = sys.argv[1]
    file_extension = sys.argv[2]
    if "." not in file_extension:
        file_extension = "." + file_extension

    shinvfile = ""
    hostname = "Unable to parse out hostname!!"

    sitevlans = []
    text_files = [f for f in os.listdir(path) if f.endswith(file_extension)]

    outfile = open("get-vlan-output.txt","w")
    outfile.write("Vlan Key, Hostname, Vlan Number, Vlan Name, Vlan IP, Vlan Mask, Vlan Description, Vlan Interface Count, VRF, Vlan Notes, Exclude dot1x (Yes/No) \n")



    for filename in text_files:
        print "Processing VLANs in file: ",filename
        # This list will hold all the times each vlan was applied to an interface by looking at the " switchport access vlan" command
        # At the end we will tally up all the times a vlan was used on an interface for the vlan_count totals
        vlancountlist=[]


        shinvfile = os.path.join(path, filename)
        shinvfh=open(shinvfile)

        shlines=shinvfh.readlines()
        numshlines=len(shlines)

        # For each file gather the relevant attributes for the vlan:  hostname[0], vlan_num[1], vlan_name[2], vlan_ip[3], vlan_mask[4], vlan_desc [5] vlan_count[6], vrf[7], vlan_notes[7]
        hostname = ""
        vlan_num = ""
        vlan_name = ""
        vlan_ip = ""
        vlan_mask = ""
        vlan_desc = ""
        vlan_count = 0
        vlan_notes = ""
        next_line = ""
        first3lines =[]
        svi_ip = ""
        svi_mask = ""

        # This dictionary will hold all the above attributes for a vlan in this file
        vlans ={}

        for i in range(0,numshlines):


            #Look for the hostname in this show command file
            if re.match("^hostname(.*)", shlines[i]):
                host = shlines[i]
                host = host.rstrip()
                # split the hostname line into two variables
                host1 = host.split(" ")
                hostname = host1[1]

                #All switches have an inherent Vlan 1
                vlans["1"] = [hostname, "1", "", "", "", "", 0, "", ""]

            # If the line in this show command file is part of the vlan configuration
            if re.match("^vlan\s+\d+", shlines[i]):
                # Save the next list as it may have the Vlan name
                #print shlines[i]
                next_line = shlines[i+1]
                #print next_line

                # Check to see if its a vlan definition by number or range
                if "," or "-" in shlines[i]:
                    vlan_name = "No name - Numbers only or range"
                    nums_only = shlines[i].split("vlan")
                    #print nums_only[1]
                    nums_only = nums_only[1].split(",")
                    #print nums_only
                    for i in range(0,len(nums_only)):
                        if "-" not in nums_only[i]:
                            num_only = nums_only[i].strip()
                            vlans[num_only] = [hostname, num_only, "", "", "", "", 0, "", ""]
                            sitevlans.append(num_only)
                        else:
                            vranges = nums_only[i].split("-")
                            vrangestart = vranges[0].strip()
                            vrangeend = vranges[1].strip()
                            vrstartint = int(vrangestart)
                            vrendint = int(vrangeend)

                            for i in range(vrstartint, vrendint+1):
                                vrstr = str(i).strip()
                                vlans[vrstr] = [hostname, vrstr, "", "", "", "", 0, "", ""]
                # Otherwise its a standard single vlan definition statement "vlan 666"
                else:
                    nums_only = shlines[i].split("vlan")
                    num_only = nums_only[i].strip()
                    vlans[num_only] = [hostname, num_only,"", "", "", "", 0, "", ""]
                    sitevlans.append(num_only)

                if re.match(" name", next_line):
                    #print shlines[i+1]
                    vlan_name_line = next_line.strip()
                    vlan_name = vlan_name_line.split("name")
                    #print vlan_name[1]
                    vlans[num_only][2] = vlan_name[1]


            # Count number of interfaces in a vlan
            if re.match("^ switchport access vlan", shlines[i]):
                vl = shlines[i].split("vlan")
                vl1 = vl[1].strip()
                vlancountlist.append(vl1)
                #print vlancountlist


            # Check to see if there is an SVI
            if re.match("^interface Vlan(.*)", shlines[i]):
                first3lines =[]
                #print shlines[i]
                next_line = shlines[i+1]
                #Is it an SVI
                svil = shlines[i].split("Vlan")
                svi1 = svil[1].strip()
                #print svi1
                first3lines.append(next_line.strip())
                first3lines.append(shlines[i+2].strip())
                first3lines.append(shlines[i+3].strip())

                if re.match("^ ip address", next_line):
                    #print "file: ", filename
                    #print "BEFORE:", svi_ip
                    #print svi_mask
                    svi_nets = next_line.split(" ")
                    svi_ip = svi_nets[3].strip()
                    # If line - ip address dhcp
                    if len(svi_nets) == 5:
                        svi_mask = svi_nets[4].strip()
                    else:
                        svi_mask = "No Mask Found"
                    #print "AFTER: ", svi_ip
                    #print svi_mask

                    # If the vlan (key) is in the vlans dictionary then it has been defined at L2
                    if svi1 in vlans:
                        vlans[svi1][3] = svi_ip
                        vlans[svi1][4] = svi_mask
                    # If the vlan is not in the vlans dictionary then it did not get defined at L2, we need to add it to the dcit and so note
                    else:
                        vlans[svi1] = [hostname, svi1, "", svi_ip, svi_mask, "", 0, "", "Vlan not defined, only SVI, CleanUp?"]
                else:

                    # If the vlan (key) is in the vlans dictionary then it has been defined at L2
                    if svi1 in vlans:
                        vlans[svi1][8] = first3lines
                    # If the vlan is not in the vlans dictionary then it did not get defined at L2, we need to add it to the dcit and so note
                    else:
                        vlans[svi1] = [hostname, svi1, "", svi_ip, svi_mask, "", 0, "", "Vlan not defined, only SVI, CleanUp?"]




        counts = dict((k, vlancountlist.count(k)) for k in set(vlancountlist))
        #print counts

        for vlan, vlan_count in counts.iteritems():
            if vlan in vlans:
                vlans[vlan][6] = vlan_count
            else:
                print "Vlan not in dictionary"
        #print vlans

        # Parse the Notes list for SVI IP address, description, and/or vrf
        for vl, vlnotes in vlans.iteritems():
            vlnote = vlnotes[8]
            #print vlnote
            #print str(len(vlnote))
            for i in range(0,len(vlnote)):

                if "description" in vlnote[i]:
                    #print "catch desc element"
                    #print vlnote[i]
                    svi_descs =  vlnote[i].split("description")
                    #print svi_descs
                    svi_desc = svi_descs[1].strip()
                    vlans[vl][5] = svi_desc
                    #print svi_desc
                    #print "-------"


                #if re.match("ip address\s\d+ ", vlnote[i]):
                if "ip address " in vlnote[i]:
                    #print "catch ip address"
                    #print vlnote[i]
                    svi_nets = vlnote[i].split(" ")
                    svi_ip = svi_nets[2].strip()
                    #print "svi_ip",svi_ip
                    if "/" in svi_nets[2]:
                        svi_slashs = svi_nets[2].split("/")
                        svi_mask = svi_slashs[1]
                    else:
                        svi_mask = svi_nets[3].strip()

                    vlans[vl][3] = svi_ip
                    vlans[vl][4] = svi_mask
                    #print vlans[vl][3]
                    #print vlans[vl][4]

                if "forwarding" in vlnote[i]:
                    #print "catch vrf"
                    #print vlnote[i]
                    svi_vrfs = vlnote[i].split(" ")
                    if "ip" in vlnote[i]:
                        svi_vrf = svi_vrfs[3].strip()
                        vlans[vl][7] = svi_vrf

                    else:
                        #svi_vrfs = vlnote[i].split(" ")
                        svi_vrf = svi_vrfs[2].strip()
                        vlans[vl][7] = svi_vrf
                    #print svi_vrf


        for vl, vlattrib in vlans.iteritems():
            #print type(vlattrib[6])
            #print type(vlattrib[7])
            #print type(vlattrib[8])
            #print "#######values"
            #print vl
            #print vlattrib[0]
            #print vlattrib[1]
            #print vlattrib[2]
            #print vlattrib[3]
            #print "attrib 5"
            #print vlattrib[4]
            #print vlattrib[5]
            #print str(vlattrib[6])
            #print vlattrib[7]
            #print vlattrib[8]
            test = str(vlattrib[6]) + "," + vlattrib[7] + "," + str(vlattrib[8])
            outfileline = vl + "," + vlattrib[0] + "," + vlattrib[1] + "," + vlattrib[2] + "," + vlattrib[3] + "," + vlattrib[4] + "," + vlattrib[5] + "," + test + "\n"
            #outfileline = vl + "," + vlattrib[0] + "," + vlattrib[1] + "," + vlattrib[2] + "," + vlattrib[3] + "," + vlattrib[4] + "," + vlattrib[5] + ","  + "\n"
            #print outfileline
            outfile.write(outfileline)

        shinvfh.close()

    outfile.close()
    #print sitevlans
    print "CSV file get-vlan-output.txt created in directory where program was executed."


# Standard call to the main() function.
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print '\nUsage: get_vlans.py.py <full path to directory of files to process> <show command output file name extension (.txt, .log, etc)\nExample:  python get_vlans.py "/Users/Claudia/Box Sync/Network Transformation/Sites/North America - Year One/96-East_Peoria/show commands" "txt"\n\n'
        sys.exit()
    else:
        main()

