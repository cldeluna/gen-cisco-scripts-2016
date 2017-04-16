#!/usr/bin/python -tt
# Project: gen-cisco-scripts
# Filename: txtfsm_ios_parsing
# claud
# PyCharm
__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "2/11/2017"
__copyright__ = "Copyright (c) 2016 Claudia"
__license__ = "Python"

import argparse
import datetime
import shinv_parser
import os
import sys
import csv
import re
import textfsm



def read_files_in_dir(dir, ext):

    valid_file_list = []

    try:
        dir_list = os.listdir(dir)
        # other code goes here, it iterates through the list of files in the directory

        for afile in dir_list:

            filename, file_ext = os.path.splitext(afile)
            #print filename, file_ext

            if file_ext.lower() in ext:
                afile_fullpath = os.path.join(dir,afile)
                valid_file_list.append(afile_fullpath)

    except WindowsError as winErr:

        print("Directory error: " + str((winErr)))
        print sys.exit("Aborting Program Execution")

    return valid_file_list, dir_list


def open_file(filename, mode):

    file_handle = ''
    # Mode = r | w | a | r+
    try:
        file_handle = open(filename, mode)

    except IOError:
        print "IOError" + str(IOError)
        print "Could not open file. Please make sure all result files are closed!"

    return file_handle


def text_fsm_parse(template_fn, data):

    # Run the text through the FSM.
    # The argument 'template' is a file handle and 'raw_text_data' is a
    # string with the content from the show_inventory.txt file
    template = open(template_fn)
    re_table = textfsm.TextFSM(template)
    fsm_results = re_table.ParseText(data)

    return fsm_results, re_table

def main():

    # Timestamp the start of the run so that a total run time can be calcuated at the end
    start_time = datetime.datetime.now()

    # Keep a list of any files that did not have any show inventory information
    no_inventory = []

    # Mandatory argument passed to script - either a filename or a directory of files to process
    path = arguments.filename

    file_list = []
    fsm_all_results = []

    if os.path.exists(path):
        if os.path.isdir(path):
            print "Processing Directory: " + path
            file_list, total_files = read_files_in_dir(path, ".log, .txt")
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
        print "Problem with path or filename!"
        print sys.exit("Aborting Program Execution due to bad file or directory argument.")


    # Open the CSV file to store results
    csv_results_fh = open_file(results_dir, 'wb')
    csv_writer = csv.writer(csv_results_fh, quoting=csv.QUOTE_MINIMAL)
    # header = ['hostname', 'filename', 'NAME', 'DESC', 'PID', 'VID', 'SN', 'Device Inventory Total', "Notes", 'Device SN']
    # csv_writer.writerow(header)

    # Iterate through the valid file list. If the script was passed a filename it will be a file_list of 1
    # If the script was passed a directory
    for fil in file_list:

        print "Processing device file: " + fil

        # open_file function returns a file handle
        fh = open_file(fil, 'r')

        # Read the file contents into a variable for parsing
        file_contents = fh.read()

        template = "textfsm_ios_shinv.template"

        fil_results, table = text_fsm_parse(template, file_contents)

        fsm_all_results.append(fil_results)

        if len(fil_results) == 0:
            no_inventory.append(fil)


    # Display result as CSV and write it to the output file
    # First the column headers...
    csv_writer.writerow(table.header)


    # ...now all row's which were parsed by TextFSM
    counter = 0
    for row in fsm_all_results:
        #print(row)
        for s in row:
            csv_writer.writerow(s)
        counter += 1
    print("Write %d records" % counter)

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
            msg = "\t" + str(file)
            print msg
            msg_csv_format = [msg, '', '', '', '', '', '', '', '']
            csv_writer.writerow(msg_csv_format)

    msg = "\nResults file created in " + results_dir
    print msg
    msg_csv_format = [msg, '', '', '', '', '', '', '', '']
    csv_writer.writerow(msg_csv_format)


    elapsed_time = datetime.datetime.now() - start_time
    msg = "Elapsed time: {}".format(elapsed_time)
    print "-" * 60
    print msg
    print "-" * 60


# Standard call to the main() function.
if __name__ == '__main__':
    # Standard call to the main() function.
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="TextFSM parser",
                                         epilog="Usage: 'python txtfsm_ios_parsing.py <filename or directory of files to parse> ")

        parser.add_argument('filename', help='filename or directory of files to parse')
        parser.add_argument('-i', '--infentory', help='Parse for show inventory output', action='store_true', default=False)

        arguments = parser.parse_args()
        main()


