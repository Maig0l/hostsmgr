#!/usr/bin/python3

from   time     import sleep
from   datetime import datetime as dt
import simplejson as json
import sys
import os


SCRIPT_DIR  = os.path.dirname(
                        os.path.realpath(__file__)) + "/"
GROUPS_FILE = SCRIPT_DIR + "groups.json"
CRON_FILE   = SCRIPT_DIR + "cron.tsv"
DST_IP      = "127.0.0.1"

args   = sys.argv[1:]
groups = json.loads(
                open(GROUPS_FILE, "r").read())

with open(CRON_FILE, 'r') as cronF:
    jobs = []
    for line in cronF:
        # Allow comments and blank lines
        if line[0] == '#' or line[0] == '\n':
            continue

        # Delete newline characters
        line = line[:-1]
        columns = line.split('\t')

        jobDict = {    "dow":     columns[0].split(','),
                      "hour": int(columns[1]),
                    "minute": int(columns[2]),
                   "command":     columns[3],
                    "groups":     columns[4].split(',')}

        jobs.append(jobDict)


def hostFormat(host, dstIp=DST_IP):
    return f"{dstIp}\t{host}\n"

# Takes an array [hour, minute] and sleeps until
#  that time of day.
def checkTime(dstHour, dstMinute):
    now   = dt.now()
    until = dt(now.year, now.month, now.day,
               dstHour,  dstMinute,
               0, now.microsecond)

    if (  now.hour == until.hour and
        now.minute == until.minute):
        return True
    return False

def execJobs():
    weekday = dt.now().isoweekday()

    for job in jobs:
        if weekday in job["dow"] or \
               '*' in job["dow"]:

            if checkTime(job["hour"],
                         job["minute"]):

                if   job["command"] == "block":
                    changeGroupState(job["groups"], True)
                elif job["command"] == "unblock":
                    changeGroupState(job["groups"], False)
                else:
                    raise Exception("Invalid command in cron.tsv")

# Returns entire new hosts file (string)
def makeFile(verbose=False):
    result =  hostFormat("localhost", "127.0.0.1")
    result += hostFormat(os.uname()[1], "127.0.0.1")

    for name in groups:
        # First item is a boolean indicating enabled state
        if groups[name][0]:
            result += f"\n# {name}\n"

            for host in groups[name][1:]:
                result += hostFormat(host)

            if verbose:
                print(f"Blocked {name}")

    return result

# Writes changes to groups file
def updateGroupsFile():
    open(GROUPS_FILE, "w").write(
                            json.dumps(groups))

# Check if group exists.
# If not, create it.
def checkGroup(name):
    if name not in groups:
        groups[name] = [True]

def addToGroup(group, hosts):
    checkGroup(group)

    if   isinstance(hosts, list):
        for host in hosts:
            groups[group].append(host)
    elif isinstance(hosts, str):
            groups[group].append(hosts)

    updateGroupsFile()

# Appends all lines from a file to a group
#  and saves to groups.json
def addFromFile(group, filename):
    checkGroup(group)

    with open(filename, "r") as newHosts:
        for line in newHosts.read():
            groups[group].append(line)

    updateGroupsFile()

def removeGroup(group):
    try:
        groups.pop(group)
        updateGroupsFile()
    except KeyError:
        exit(f" /!\ Group {group} doesn't exit.")

# Assigns new boolean value to the first
#  item of a group.
def changeGroupState(group, newState):
    try:
        if isinstance(group, str):
            groups[group][0] = newState

        if isinstance(group, list):
            for name in group:
                groups[name][0] = newState

        updateGroupsFile()
    except KeyError:
        exit(f" /!\ Group {group} doesn't exit.")


## Command-line interface
try:
    verb = args[0]
except IndexError:
    exit(" /!\ Not enough arguments.")

# add website domain1.com domain2.com
if   verb == "add":
    addToGroup(args[1], args[2:])

# remove website
elif verb == "remove":
    removeGroup(args[1])

# addbulk website blockList.txt
elif verb == "addbulk":
    # Read from standard input
    if args[2] == "-":
        for line in sys.stdin:
            addToGroup(args[1], line.rstrip())
    else:
        addFromFile(args[1], args[2])

# [block|unblock] website
elif verb == "block":
    changeGroupState(args[1], True)
elif verb == "unblock":
    changeGroupState(args[1], False)

# Prints groups and whether or not they're enabled.
# If an argument is given, prints all the hosts the group contains.
# list [group]
elif verb == "list":
    try:
        group = args[1]
        allItems = ""
        for item in groups[group][1:]:
            allItems += item + "\n"
        os.system(f"echo '{allItems}' | less")

    except IndexError:
        for name in groups:
            print(f"[{'*' if groups[name][0] else ' '}] {name}")

# make [filename]
elif verb == "make":
    try:
        filename = args[1]
        with open(filename, "w+") as hostsFile:
            hostsFile.write(
                        makeFile(verbose=True))

    except IndexError:
        print(makeFile())
        pass

elif verb == "daemon":
    import daemon
    
    with daemon.DaemonContext():
        while True:
            execJobs()
            sleep(60)

else:
    exit(f" /!\ Unknown command: `{verb}`")

