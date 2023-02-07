#!/usr/bin/env python3
import sys
import json
import yaml


def print_trufflehog_output(y):
    output = {}
    for i in y["patterns"]:
        if i["pattern"]["confidence"] != "high":
            continue
        output.update({i["pattern"]["name"]: i["pattern"]["regex"]})

    print(json.dumps(output, indent=4, sort_keys=True))


def print_gitleaks_output(y):
    s = 'title = "gitleaks config"'

    for i in y["patterns"]:
        if i["pattern"]["confidence"] != "high":
            continue
        s += f"""
[[rules]]
    description = '''{i["pattern"]["name"]}'''
    regex = '''{i["pattern"]["regex"]}'''
    tags = ["secret"]
"""
    print(s)


def main():

    if len(sys.argv) < 3:
        print(f"\nUsage:\n\t{sys.argv[0]} [regex-db.yml] [output-type]")
        print("Supported output types: trufflehog, gitleaks")
        exit(1)

    f = open(sys.argv[1], "r")
    y = yaml.safe_load(f.read())
    f.close()

    OUTPUT_TYPE = sys.argv[2]
    if OUTPUT_TYPE not in ("trufflehog", "gitleaks"):
        print("Invalid output type")
        exit(1)
    if OUTPUT_TYPE == "trufflehog":
        print_trufflehog_output(y)
    elif OUTPUT_TYPE == "gitleaks":
        print_gitleaks_output(y)


if __name__ == "__main__":
    main()
