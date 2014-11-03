#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# License: GNU LGPL v3
"""
Get efrei timetables

Usage: timetable [-h] [-j] [-m] [-f FILE] [PERIOD]

Arguments:
    PERIOD     Prints timetable for a given period
               Default is to print all available informations

Options:
    -h, --help          Print this help and exit
    -j, --json          Print data in the JSON format
    -m, --manual        Do not use automatic login
    -f, --file FILE     Use FILE to find credential
                        Default is the 'credentials' in the HOME directory

Examples:
    timetable  0        : print today
    timetable  2        : print today, tomorrow and the day after
    timetable  next     : print the next course
    timetable  previous : print the previous course
    timetable  current  : print the current course
"""

import os
import sys
import time
import base64
import datetime
import getpass
from docopt import docopt
from extranet import Extranet

# To use french names
#DAYS   = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
#MONTHS = ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin",
#          "Juil", "Aou", "Sep", "Oct", "Nov", "Dec"]

DAYS   = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def print_courses(courses):
    for c in courses:
        print(c["title"])
        print("    ", c["room"])
        print("    ", period(c["start"], c["end"]))
        print()


def period(start, end, *, days=DAYS, months=MONTHS):
    return "{wday} {day} {mon}: {sh}h{sm}-{eh}h{em}".format(
                wday = days[int(start.weekday())],
                day  = start.day,
                mon  = months[int(start.month)-1],
                sh   = start.hour,
                sm   = start.minute,
                eh   = end.hour,
                em   = end.minute)


def today():
    return datetime.datetime.fromtimestamp(time.time())


def filter_dates(timetable, selection):
    if selection is None:
        return timetable

    if selection == "previous":
        timetable.reverse()
        for course in timetable:
            if today().timestamp() > course["end"].timestamp():
                return [course]
        return []

    if selection == "current":
        for course in timetable:
            if (course["start"].timestamp() < today().timestamp()
                                            < course["end"].timestamp()):
                return [course]
        return []

    if selection == "next":
        for course in timetable:
            if today().timestamp() < course["start"].timestamp():
                return [course]
        return []


    try:
        return [ x for x in timetable
                   if x["start"].day <= today().day + int(selection) ]
    except ValueError as e:
        sys.exit("Invalid command: " + selection)


def converted_dates(timetable):
    for course in timetable:
        course["start"] = course["start"].timestamp()
        course["end"]   = course["end"].timestamp()

    return timetable



def main():
    args = docopt(__doc__)

    cred_file = args["--file"] or "%s/.credentials" % os.environ["HOME"]

    if args["--manual"]:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    else:
        # No encryption, just avoid grepping
        with open(cred_file) as f:
            username = base64.b64decode(f.readline()[:-1])
            password = base64.b64decode(f.readline()[:-1])


    timetable = Extranet(username, password).get_timetable()

    # Sort timetable chronologically
    timetable.sort(key=lambda x: x["start"].timestamp())

    timetable = filter_dates(timetable, args["PERIOD"])


    if args["--json"]:
        print(converted_dates(timetable))
    else:
        print_courses(timetable)

if __name__ == "__main__":
    main()
