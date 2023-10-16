#!/usr/bin/env python3
import yaml
import sys
import re

if len(sys.argv) < 2:
    print(f"\nUsage:\n\t{sys.argv[0]} [regex-db.yml]")
    exit(1)
with open(sys.argv[1], 'r') as stream:
    y = yaml.safe_load(stream)


assert type(y) == dict
assert "patterns" in y

all_regexes = []
all_names = []
for i in y["patterns"]:
    print(i)
    assert "pattern" in i
    assert type(i["pattern"]) == dict
    assert "name" in i["pattern"]
    assert "regex" in i["pattern"]
    assert "confidence" in i["pattern"]
    assert i["pattern"]["confidence"] in ("low", "high")

    r = i["pattern"]["regex"]
    name = i["pattern"]["name"]

    # check for invalid regex
    re.compile(r)

    # check for duplicated regexes
    if r in all_regexes:
        raise ValueError("Repeated regex")
    all_regexes.append(r)

    # check for duplicated names
    if name.lower() in all_names:
        raise ValueError("Duplicated name")
    all_names.append(name.lower())

print("\n✅ CI Passed!")
