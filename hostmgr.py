#!/usr/bin/python3

import simplejson as json
import sys
import os


GROUPS_FILE = "groups.json"
args   = sys.argv[1:]
groups = json.loads(
                open(GROUPS_FILE, "r").read())

def hostFormat(host):
    return f"127.0.0.1\t{host}\n"

# Returns entire new hosts file (string)
def makeFile():
    result = hostFormat("localhost") + "\n"

    for name in groups:
        # First item is a boolean indicating enabled state
        if groups[name][0]:
            result += f"# {name}\n"

            for host in groups[name][1:-1]:
                result += hostFormat(host)
            print(f"Enabled {name}")

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
        groups[group][0] = newState
        updateGroupsFile()
    except KeyError:
        exit(f" /!\ Group {group} doesn't exit.")


## Command-line interface
verb = args[0]

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

# [enable|disable] website
elif verb == "enable":
    changeGroupState(args[1], True)
elif verb == "disable":
    changeGroupState(args[1], False)

elif verb == "list":
    try:
        allItems = ""
        for item in groups[args[1]][1:]:
            allItems += item + "\n"
        os.system(f"echo '{allItems}' | less")
    except IndexError:
        for name in groups:
            print(f"[{'*' if groups[name][0] else ' '}] {name}")

else:
    exit(f" /!\ Unknown command: `{verb}`")
