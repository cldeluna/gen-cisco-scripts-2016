#!/usr/bin/python -tt
# get-cdp-info
# Claudia
# PyCharm
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "2/10/16  6:09 AM"
__copyright__ = "Copyright (c) 2015 Claudia de Luna"
__license__ = "Python"



import sys
import re
import os
#import xlwt
#import xlrd
#from xlutils.copy import copy
from collections import Counter


def file_accessible(filepath, mode):
    ''' Check if a file exists and is accessible. '''
    try:
        f = open(filepath, mode)
        f.close()
    except IOError as e:
        return False

    return True


def cdp(showfile, outfilebld):
    lhostname = ""
    rhostname = ""
    incdpinfo = 0
    cdpinfo = []
    cdpinfod = {}
    rcount = 0
    scount = 0
    look = ""


    #print "in the function", base_path
    #print "in the function showfile ", showfile

    # Absolute path to an individual show commands file for processing
    sfile = open(showfile,"r")

    # Append to Text file generated in main.
    #print outfilebld
    outfile = open(outfilebld,"a")


    # Process each line in the show command text file passed from main
    for line in sfile:
        #print("line: {}".format(line))

        #Look for the hostname
        if re.match("^hostname(.*)", line):
            host=line
            host = host.rstrip()
            # split the hostname line into two variables
            host1=host.split(" ")
            lhostname = host1[1]
            #print "Matched Hostname"
            #print lhostname

        if re.match("^Device ID:", line) and not incdpinfo:
            cdpinfo = []
            cdpinfod = {}
            incdpinfo = 1
            look = ""
            host=line.rstrip()
            host1=host.split(":")
            rhostname = host1[1].strip()
            #print rhostname
            #print "Matched Device ID"

        # If InCDPInfo is set and if its not a blank line add the line to the list cdpinfo
        if incdpinfo and line not in ['\n', '\r\n']:
            #cdpinfo.append(line.rstrip().split(":"))
            cdpinfo.append(line.rstrip())
            #print len(cdpinfo) , cdpinfo
            #print "Matched incdpinfo and not empty line"
            if "Router" in line:
                rcount = rcount + 1
            if "Switch" in line:
                scount = scount + 1

        #if incdpinfo and "IP address:" in line:
            #print "FOUND IP" ,
            #print line
            #cdpinfo.append(line.strip())

            #print cdpinfo

        # If its a cdp neig delimeter line "-------" reset In CDP Info and process the list into a dictionary
        if (re.match("^(-){7,25}", line) or re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)) and incdpinfo == 1:
        #if re.match("^(-){20,25}", line) and incdpinfo == 1:
        #if (re.match("^Device ID:", line) or re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)) and incdpinfo == 1:
            incdpinfo=0
            #print "Matched ---- now Zero"
            #print("line: {}".format(line))
            #print re.match("^\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", line)
            #print re.match("^-{2,25}", line)
            for i in range (len(cdpinfo)):
                #print line
                # If there is one comma in the line then its a multi key/value pair line and it needs to be split
                if cdpinfo[i].count(",") == 1 :
                    cdpinfod["local_hostname"] = lhostname
                    cdpinfod["remote_hostname"] = rhostname
                    cdpinfod["filename"] = showfile

                    multikey = cdpinfo[i].split(",")


                    for j in range (len(multikey)):
                        #print multikey[j]
                        #print "!"*80
                        #print cdpinfo[i]
                        cntr = Counter(cdpinfo[i])
                        #print "Counter ",cntr
                        #print cntr[':']

                        if re.match("[\w\s]*:\s*\w",cdpinfo[i]) and cntr[':']==2:
                            if "ucast" not in cdpinfo[i]:
                                #print "mutlikey", multikey[j]
                                cdpkey, cdpvalue = multikey[j].split(":")
                                cdpinfod[cdpkey.strip()] = cdpvalue.strip()


                elif re.match("\w[\s\)]?:\s+.", cdpinfo[i]):
                    cdpinfod["local_hostname"] = lhostname
                    cdpinfod["remote_hostname"] = rhostname
                    cdpinfod["filename"] = showfile
                    cdpkey, cdpvalue = cdpinfo[i].split(":")
                    cdpinfod[cdpkey.strip()] = cdpvalue.strip()


            if len(cdpinfod) > 0:

                #print("CDP INFO Dictionary: {}".format(cdpinfod))
                #print "Length of Dict; ",
                #print len(cdpinfod)
                #print "COUNTS:"+ str(rcount) + " " + str(scount)
                if rcount > 2 or scount > 2:
                    look = "Multiple Routing (" + str(rcount) +") and/or Switching (" + str(scount) +") CDP Neighbors"
                    #print "LOOK: " + look
                if 'Capabilities' in cdpinfod.keys() and 'Platform' in cdpinfod.keys():

                    string = lhostname + ", " + cdpinfod['Interface']  + ", " + rhostname + ", " + cdpinfod['Port ID (outgoing port)'] + ", " + cdpinfod['Capabilities'] + ", " + cdpinfod['Platform']+ ", " + cdpinfod['filename'] + ", " + look + "\n"
                else:
                    string = lhostname + ", " + cdpinfod['Interface']  + ", " + rhostname + ", " + cdpinfod['Port ID (outgoing port)'] + ", " + " "                      + ", " + " "                 + ", " + cdpinfod['filename'] + ", " + look + "\n"

                #print string
                outfile.write(string)
                #outfile.write("\n")
                #print "About to write %s to sheet after row %d" % (string, r)



    # Close all the files we opened/created
    sfile.close()
    outfile.close()




# Provided main() calls the above functions
def main():
    # Take path argument and list all text files
    """
    Consolidate CDP Information from show command files
    :return:
    """

    shcmd_dir = sys.argv[1]
    location_info = sys.argv[2].strip()

    print "Using Show Commands Directory: ",shcmd_dir




    #shcmd_dir = "show commands"
    #outpath = os.path.join(base_path, psa_dir, "cdp-output.csv")
    outpath = location_info + "-CDP-REPORT.csv"
    #print "in main" , path
    text_files = [f for f in os.listdir(shcmd_dir) if f.endswith('.txt') or f.endswith('.log')]
    tflen = len(text_files)
    #print str(tflen)
    #print "Local Hostname," + "Remote Hostname," "Fiile," + "CDP Info"
    header = ["CDP Local Hostname", " CDP Local Interface", "CDP Remote Hostname", "CDP Remote Port ID (outgoing port)", "Capabilities", "Remote Platform/Model", "Config File Processed", "Notes", "Local Found in Survey", "Remote Found in Survey", "Local Found in Area51", "Remote Found in Area51"]
    outfile = open(outpath,"a")
    outfile.write(str(header))
    outfile.write("\n")
    outfile.close()

    for filename in text_files:
        print "Processing show command file: ", filename
        fullpath = os.path.join(shcmd_dir, filename)
        #print fullpath
        cdp(fullpath, outpath)




# Standard call to the main() function.
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print '\nUsage: get-cdp-info.py <path to base directory of site> <File name prefix> \nExample: python cdp_sum.py "/Users/Claudia/dir/path/to/show/commands" "SiteX" "\n\n'
        sys.exit()
    else:
        main()

