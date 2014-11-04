#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# License: GNU LGPL v3
"""
Get efrei timetables

Usage: timetable [-h] [-j] [-m] [-s] [-f FILE] [PERIOD]

Arguments:
    PERIOD     Prints timetable for a given period
               Default is to print all available informations

Options:
    -h, --help          Print this help and exit
    -j, --json          Print data in the JSON format
    -m, --manual        Do not use automatic login
    -s, --save          Save password to keyring.
                        Needs to be combined with --manual
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
import datetime
import getpass
from docopt import docopt
from extranet import Extranet
import keyring

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


def now():
    return datetime.datetime.fromtimestamp(time.time())


def courses_in_range(start, end, num, timetable):
    result    = []
    start_lim = start
    end_lim   = end

    for course in timetable:
        if num == 0:
            break

        if type(start) == str:
            start_lim = course[start].timestamp()

        if type(end) == str:
            end_lim = course[end].timestamp()

        if start_lim < now().timestamp() <= end_lim:
            result.append(course)
            num -= 1

    return result


def filter_dates(timetable, selection):
    if selection is None:
        return timetable

    if selection == "previous":
        timetable.reverse()
        return courses_in_range("end", now().timestamp(), 1, timetable)

    if selection == "current":
        return courses_in_range("start", "end", 1, timetable)

    if selection == "next":
        return courses_in_range(0, "start", 1, timetable)

    try:
        return [ x for x in timetable
                   if x["start"].day <= now().day + int(selection) ]
    except ValueError as e:
        sys.exit("Invalid command: " + selection)


def converted_dates(timetable):
    for course in timetable:
        course["start"] = course["start"].timestamp()
        course["end"]   = course["end"].timestamp()

    return timetable



def main():
    args = docopt(__doc__)

    cred_file = args["--file"] or "%s/.extranet" % os.environ["HOME"]

    if not os.path.exists(cred_file):
        open(cred_file, 'w').close()

    if args["--manual"]:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        if "--save" in args:
            with open(cred_file, 'w') as f:
                f.write(username + '\n')
                keyring.set_password("extranet", username, password)

    else:
        # No encryption, just avoid grepping
        with open(cred_file) as f:
            username = f.readline()[:-1]
            password = keyring.get_password("extranet", username)


    try:
        timetable = Extranet(username, password).get_timetable()
    except ValueError as e:
        exit("\nAuthentication failed.\n"
           + "If no password has been saved yet, please, try:\n"
           + "\ttimetable.py -ms")

    # Sort timetable chronologically
    timetable.sort(key=lambda x: x["start"].timestamp())

    timetable = filter_dates(timetable, args["PERIOD"])


    if args["--json"]:
        print(converted_dates(timetable))
    else:
        print_courses(timetable)

if __name__ == "__main__":
    main()
