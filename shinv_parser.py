#!/usr/bin/python -tt
# Project: 2016
# Filename: shinv_parser
# claud
# PyCharm
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "2/7/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"



import os
import sys
import csv
import datetime
from pyparsing import *
import argparse

#from pyparsing import Word, Keyword, nums, OneOrMore, Optional, Suppress, Literal, alphanums, LineEnd, LineStart, Group, ParserElement





def read_files_in_dir(dir, ext):

    valid_file_list = []

    try:
        dir_list = os.listdir(dir)
        # other code goes here, it iterates through the list of files in the directory

        for afile in dir_list:

            filename, file_ext = os.path.splitext(afile)
            #print filename, file_ext

            if file_ext.lower() == ext.lower():
                afile_fullpath = os.path.join(dir,afile)
                valid_file_list.append(afile_fullpath)

        #print valid_file_list


    except WindowsError as winErr:

        print("Directory error: " + str((winErr)))
        print sys.exit("Aborting Program Execution")

    return valid_file_list


def open_file(filename, mode):

    # Mode = r | w | a | r+

    try:
        file_handle = open(filename, mode)

    except IOError:
        print "IOError" + str(IOError)

    return file_handle


def get_hostname(data):

    hostname = 'Unable to parse hostname'
    h = Literal('hostname')
    s = Literal('switchname')

    a = Word(alphanums)
    u = ZeroOrMore("_")
    d = ZeroOrMore("-")
    p = ZeroOrMore(".")

    hostname_key = h | s
    #hostname_spclchar = u | p | d
    hostname_spclchar = oneOf("_ - .")

    hostname_value = Combine(a + ZeroOrMore(hostname_spclchar) + ZeroOrMore(a + hostname_spclchar))

    hostname_line = hostname_key + hostname_value.setResultsName("hostname")

    hostname_token = hostname_line.scanString(data)

    for h in hostname_token:
        hostname = h[0].hostname.strip()

    return hostname

def get_device_sn(data):

    if re.search("Processor Board ID(.*)", shlines[i]):
        tmp = shlines[i].strip()
        tmp = shlines[i].split()
        id_sn = tmp[3]

    elif re.search("Motherboard serial number(.*)", shlines[i]):
        tmp = shlines[i].strip()
        tmp = shlines[i].split()
        id_sn = tmp[-1]


    elif re.search("Motherboard Serial Number(.*)", shlines[i]):
        tmp = shlines[i].strip()
        tmp = shlines[i].split()
        id_sn = tmp[-1]


def main():

    # Timestamp the start of the run so that a total run time can be calcuated at the end
    start_time = datetime.datetime.now()

    no_inventory = []
    path = arguments.filename
    good_path = False
    file_list = []

    if os.path.exists(path):
        #print os.path.exists(path)
        good_path = True
        if os.path.isdir(path):
            print "Processing Directory: " + path
            file_list = read_files_in_dir(path, ".log")
            print "\t Valid files in directory: " + str(len(file_list))
            path_list = path.split(os.sep)
            results_fn = path_list[-2] + "-results.csv"
            results_dir = os.path.join(path, results_fn)
            results_num_files = str(len(file_list))


        else:
            print "Processing File: " + path
            # read_file function returns a file handle
            file_list.append(path)
            fn, fext = os.path.splitext(path)
            results_fn = fn + "-results.csv"
            curr_dir = os.getcwd()
            results_dir = os.path.join(curr_dir, results_fn)
            results_num_files = '1'

    else:
        print "Problem with path or filename"
        print sys.exit("Aborting Program Execution")


    # Open the CSV file to store results
    csv_results_fh = open_file(results_dir, 'wb')
    csv_writer = csv.writer(csv_results_fh, quoting=csv.QUOTE_MINIMAL)
    header = ['hostname', 'filename', 'NAME', 'DESC', 'PID', 'VID', 'SN', 'Device Inventory Total', 'Device SN']
    csv_writer.writerow(header)

    # Iterate through the valid file list. If the script was passed a filename it will be a file_list of 1
    # If the script was passed a directory
    for fil in file_list:

        #print "Processing device file: " + fil

        fh = open_file(fil, 'r')
        file_contents = fh.read()

        hostname = get_hostname(file_contents)
        print hostname

        #x = raw_input("Press any key to continue")

        n = Literal('NAME')
        d = Literal('DESCR')
        p = Literal('PID')
        v = Literal('VID')
        s = Literal('SN')


        colon = Suppress(':')
        comma = Suppress(',')

        inv_nonquote = Word(alphanums + "-" + "/")
        inv_value = QuotedString('"') | inv_nonquote

        newline = Suppress(LineEnd())


        line = n + colon + inv_value.setResultsName("name") + comma + d + colon + inv_value.setResultsName("desc") + newline + p + colon + inv_value.setResultsName("pid") + comma + v + colon + inv_value.setResultsName("vid") + comma + s + colon + inv_value.setResultsName("sn")
        line.setDefaultWhitespaceChars(' \t')
        ml = line.scanString(file_contents)

        line_count = 0

        for x in ml:
            line_count += 1
              # print "\nXXXXXXXXXXXXXXXXXXXXXXXXX"
              # print x
              # print "\n"
              # print x[0]
              # print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n"
              # print x[0].name
              # print x[0].desc
              # print x[0].pid
              # print x[0].vid
              # print x[0].sn
            row = [hostname, fil, x[0].name, x[0].desc, x[0].pid, x[0].vid, x[0].sn, line_count, 'Device SN']
            csv_writer.writerow(row)

        print "Device has " + str(line_count) + " inventory items"
        if line_count == 0:
            no_inventory.append(fil)



        fh.close()

    csv_results_fh.close()


    print "Number of files processed: " + results_num_files
    print "List of files/devices without inventory information: " + str(no_inventory)
    print "Results file created in " + results_dir

    elapsed_time = datetime.datetime.now() - start_time
    print "Elapsed time: {}".format(elapsed_time)







# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cisco show inventory parser",
                                     epilog="Usage: ' python shinv_parser.py somefile.txt' ")

    parser.add_argument('filename', help='filename to parse')
    #parser.add_argument('-a', '--all', help='Execute all exercises in week 4 assignment', action='store_true',
    #                    default=False)
    arguments = parser.parse_args()
    main()


