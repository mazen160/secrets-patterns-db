# A script to remove invalid Regex and repeated values
import yaml
import sys
import re

if len(sys.argv) < 2:
    print(f"\nUsage:\n\t{sys.argv[0]} [regex-db.yml]")
    exit(1)

with open(sys.argv[1], 'r') as stream:
    y = yaml.safe_load(stream)


output = []
all_regexes = []
all_names = []
for i in y["patterns"]:
    r = i["pattern"]["regex"]
    name = i["pattern"]["name"]
    try:
        re.compile(r)
    except re.error:
        continue

    # check for duplicated regexes
    if r in all_regexes:
        # print(f"DUP-REGEX: {r}")
        continue
    all_regexes.append(r)

    # check for duplicated names
    # if name.lower() in all_names:
        # print(f"DUP: {name}")

    all_names.append(name.lower())

    output.append(i)


# print regexes
# for a in output:
#     print(a["pattern"]["regex"])


# Sort output
output = sorted(output, key=lambda i: i['pattern']['name'])


newData = {"patterns": output}

# Print YAML
# class MyDumper(yaml.Dumper):
#     def increase_indent(self, flow=False, indentless=False):
#         return super(MyDumper, self).increase_indent(flow, False)

# yaml.dump(newData, sys.stdout,
#           default_flow_style=False, Dumper=MyDumper, sort_keys=False)


# Save into JSON export
# a = json.dumps(newData)
# f = open("exported.json", "w")
# f.write(a)
# f.close()
