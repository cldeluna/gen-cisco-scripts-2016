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

import argparse
from pyparsing import *

#from pyparsing import Word, Keyword, nums, OneOrMore, Optional, Suppress, Literal, alphanums, LineEnd, LineStart, Group, ParserElement



def some_function():
    pass


def main():
    file_handle = open(arguments.filename, 'r')

    file_contents = file_handle.read()

    print file_contents



    inv_key = Word(alphas)
    inv_colon = Suppress(':')
    inv_comma = Suppress(',')
    inv_nonquote = Word(alphanums + "-" + "/")
    inv_value = QuotedString('"') | inv_nonquote
    lf = Suppress(LineEnd())

    first_element = Word('NAME') + inv_colon + inv_value + inv_comma

    pattern = OneOrMore(inv_key + inv_colon +  inv_value)

    #trying to identify the two line pattern where the first of the two lines starts with 'NAME" key
    # but not used in this example
    first_line = first_element + pattern + lf + pattern

    Line = delimitedList(pattern)

    Lines = OneOrMore(Group(Line))

    grammar = Lines

    grammar.setDefaultWhitespaceChars(" \t")

    my_list = grammar.scanString(file_contents)
    print type(my_list)

    for item in my_list:
        print type(item)
        print item[0]
        my_data = item[0][0]

    list_of_dicts = []
    tmp_dict = []

    new_module = True

    print len(my_data)

    num_modules = len(my_data)/10

    for x in range(num_modules):
        tmp = my_data[x:x+10]
        print tmp














# Standard call to the main() function.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cisco show inventory parser",
                                     epilog="Usage: ' python shinv_parser.py somefile.txt' ")

    parser.add_argument('filename', help='filename to parse')
    #parser.add_argument('-a', '--all', help='Execute all exercises in week 4 assignment', action='store_true',
    #                    default=False)
    arguments = parser.parse_args()
    main()


