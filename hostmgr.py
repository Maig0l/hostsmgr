#!/usr/bin/python3

import simplejson as json

groups = json.loads(open("hostgrps.json").read())

def hostFormat(host):
    return f"127.0.0.1\t{host}\n"

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

