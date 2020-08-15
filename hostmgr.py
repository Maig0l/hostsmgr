#!/usr/bin/python3

import simplejson as json

GROUPS_FILE = "groups.json"
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

# Appends all lines from a file to a group
#  and saves to groups.json
def addFromFile(group, filename):
    # If group doesn't exist, create and enable it
    if group not in groups:
        groups[group] = [True]

    with open(filename, "r") as newHosts:
        for line in newHosts:
            groups[group].append(line)

    updateGroupsFile()

def removeGroup(group):
    try:
        groups.pop(group)
        updateGroupsFile()
    except KeyError:
        exit(f" /!\ Group {group} doesn't exit.")

