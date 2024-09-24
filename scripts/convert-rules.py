#!/usr/bin/env python3
import sys
import json
import yaml
import argparse


def trufflehog_output(args, y):
    output = {}
    for i in y["patterns"]:
        if args.low_confidence is None and i["pattern"]["confidence"] != "high":
            continue
        output.update({i["pattern"]["name"]: i["pattern"]["regex"]})
    
    return json.dumps(output, indent=4, sort_keys=True)
    

def gitleaks_output(args, y):
    s = 'title = "gitleaks config"'

    for i in y["patterns"]:
        if args.low_confidence is None and i["pattern"]["confidence"] != "high":
            continue
        s += f"""
[[rules]]
    id = '''{i["pattern"]["name"]}'''
    description = '''{i["pattern"]["name"]}'''
    regex = '''{i["pattern"]["regex"]}'''
    keywords = ["secret"]
"""
    return s


def main(args):
    f = open(args.database_file, "r")
    y = yaml.safe_load(f.read())
    f.close()
    
    output_string = ""
    ext_string = ""
    if args.output_type == "trufflehog":
        output_string = trufflehog_output(y)
        ext_string = "json"
    elif args.output_type == "gitleaks":
        output_string = gitleaks_output(args, y)
        ext_string = "toml"
    
    if args.export_filename is not None:              
        f = open(f"{args.export_filename}.{ext_string}", "w")
        f.write(output_string)
        f.close()
    else:
        print(output_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert yaml database file to rules for trufflehog or gitleaks')
    parser.add_argument("--db", dest = "database_file", required = True, help = "The yaml database file")
    parser.add_argument("--type", dest= "output_type", required = True, choices=['trufflehog', 'gitleaks'], help = "Supported output types: trufflehog, gitleaks")
    parser.add_argument('-e', '--export', dest="export_filename", help = "Give filename, extension toml/json will be added")
    parser.add_argument('-l', '--low_confidence', help = "Add low confidence entries", action='store_true')
    args = parser.parse_args()
    
    main(args)
