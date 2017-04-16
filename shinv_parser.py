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
import re
import textfsm

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

    return valid_file_list, dir_list


def open_file(filename, mode):

    # Mode = r | w | a | r+
    try:
        file_handle = open(filename, mode)

    except IOError:
        print "IOError" + str(IOError)
        print "Could not open file. Please make sure all result files are closed!"

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

    #hostname_value = Combine(a + ZeroOrMore(hostname_spclchar) + ZeroOrMore(a + hostname_spclchar))
    hostname_value = Word(srange("[A-Za-z0-9_\-]"))

    hostname_line = hostname_key + hostname_value.setResultsName("hostname")

    hostname_token = hostname_line.scanString(data)

    for h in hostname_token:
        hostname = h[0].hostname.strip()

    return hostname

def get_device_sn(data):

    serial_number = []

    pu = Literal('Processor Board ID')
    pl = Literal('Processor board ID')
    ml = Literal('Motherboard serial number')
    mu = Literal('Motherboard Serial Sumber')
    sn = Word(alphanums)
    colon = Suppress(":")

    key = pu | pl | ml | mu

    line = key + ZeroOrMore(colon) + sn.setResultsName("sn")

    line_token = line.scanString(data)

    for l in line_token:
        item_sn = l[0].sn.strip()
        serial_number.append(item_sn)

    return serial_number

def categorize(data):

    category = ''

    if "Transceiver" in data:
        category = "Optics"
    if "Clock Module" in data:
        category = "Clock Module"
    if "Max Buffers" in data:
        category = "Max Buffers"
    if re.search(r'[P|p]ower [S|s]upply', data):
        category = "Power Supply"

    return category


def text_fsm_parse(template_fn, data):


    # Run the text through the FSM.
    # The argument 'template' is a file handle and 'raw_text_data' is a
    # string with the content from the show_inventory.txt file
    template = open(template_fn)
    re_table = textfsm.TextFSM(template)
    fsm_results = re_table.ParseText(data)


    # Display result as CSV and write it to the output file
    # First the column headers...
    print(re_table.header)

    return fsm_results





def main():

    # Timestamp the start of the run so that a total run time can be calcuated at the end
    start_time = datetime.datetime.now()

    # Keep a list of any files that did not have any show inventory information
    no_inventory = []

    # Mandatory argument passed to script - either a filename or a directory of files to process
    path = arguments.filename

    file_list = []
    fsm_results = []

    if os.path.exists(path):
        if os.path.isdir(path):
            print "Processing Directory: " + path
            file_list, total_files = read_files_in_dir(path, ".log")
            print "\t Total files in directory: " + str(len(total_files))
            print "\t Valid files in directory: " + str(len(file_list))

            path_list = path.split(os.sep)
            results_fn = path_list[-2] + "-results.csv"
            results_dir = os.path.join(path, results_fn)
            results_num_files = str(len(file_list))

        else:
            print "Processing File: " + path
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
    header = ['hostname', 'filename', 'NAME', 'DESC', 'PID', 'VID', 'SN', 'Device Inventory Total', "Notes", 'Device SN']
    csv_writer.writerow(header)

    # Iterate through the valid file list. If the script was passed a filename it will be a file_list of 1
    # If the script was passed a directory
    for fil in file_list:

        #print "Processing device file: " + fil

        # open_file function returns a file handle
        fh = open_file(fil, 'r')

        # Read the file contents into a variable for parsing
        file_contents = fh.read()

        if arguments.textfsm:

            # Timestamp the start of the run so that a total run time can be calcuated at the end
            #start_time = datetime.datetime.now()

            # Load the input file to a variable

            raw_text_data = fh.read()
            fh.close()

            template = "textfsm_ios_shinv.template"

            output_filename = "shinv_textfsm_output.csv"

            # the results are written to a CSV file
            outfile_name = open(output_filename, "w+")
            outfile = outfile_name

            fsm_results_tmp = text_fsm_parse(template, raw_text_data)

            fsm_results.append(fsm_results_tmp)

        else:
            # Get the hostname of the device
            hostname = get_hostname(file_contents)
            print hostname,

            # Get the main SN of the device
            dev_serial_num = get_device_sn(file_contents)
            # print dev_serial_num


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

            line = n + colon + inv_value.setResultsName("name") + comma + d + colon + inv_value.setResultsName("desc") \
                   + newline \
                   + p + colon + inv_value.setResultsName("pid") + comma + v + colon + inv_value.setResultsName("vid") \
                   + comma + s + colon + inv_value.setResultsName("sn") + ZeroOrMore(newline)

            line.setDefaultWhitespaceChars(' \t')
            #line.enablePackrat()

            ml = line.scanString(file_contents)

            line_count = 0

            for x in ml:
                line_count += 1
                notes = categorize(x[0].desc)
                row = [hostname, fil, x[0].name, x[0].desc, x[0].pid, x[0].vid, x[0].sn, line_count, notes, dev_serial_num]
                csv_writer.writerow(row)


            print "\tDevice has " + str(line_count) + " inventory items"
            if line_count == 0:
                no_inventory.append(fil)

            # Close show command file
            fh.close()


            # Summary Information

            print "\n"
            print "-" * 60
            print "-" * 60
            msg = "Number of files processed: " + results_num_files
            print msg
            csv_writer.writerow("\n\n\n")
            msg_csv_format = [msg, '', '', '', '', '', '', '', '']
            csv_writer.writerow(msg_csv_format)

            if len(no_inventory) > 0:
                msg = "Number of files/devices without inventory information: " + str(len(no_inventory))
                print msg
                msg_csv_format = [msg, '', '', '', '', '', '', '', '']
                csv_writer.writerow(msg_csv_format)

                msg = "List of files/devices without inventory information: "
                print msg
                msg_csv_format = [msg, '', '', '', '', '', '', '', '']
                csv_writer.writerow(msg_csv_format)

                for file in no_inventory:
                    msg = "\t" + file
                    print msg
                    msg_csv_format = [msg, '', '', '', '', '', '', '', '']
                    csv_writer.writerow(msg_csv_format)

            msg = "\nResults file created in " + results_dir
            print msg
            msg_csv_format = [msg, '', '', '', '', '', '', '', '']
            csv_writer.writerow(msg_csv_format)


    if arguments.textfsm:
        # ...now all row's which were parsed by TextFSM
        counter = 0
        for row in fsm_results:
            print(row)
            for s in row:
                outfile.write("%s;" % s)
            outfile.write("\n")
            counter += 1
        print("Write %d records" % counter)



    elapsed_time = datetime.datetime.now() - start_time
    msg = "\nElapsed time: {}".format(elapsed_time)
    print msg
    msg_csv_format = [msg, '', '', '', '', '', '', '', '']
    csv_writer.writerow(msg_csv_format)
    print "-" * 60
    print "-" * 60

    # Close results CSV file
    csv_results_fh.close()


# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cisco show inventory parser",
                                     epilog="Usage: ' python shinv_parser.py somefile.txt' ")

    parser.add_argument('filename', help='filename to parse')
    parser.add_argument('-t', '--textfsm', help='Parse using TextFSM Module', action='store_true', default=False)

    arguments = parser.parse_args()
    main()


