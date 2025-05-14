#!/usr/bin/env python3
import sys
import json
import yaml
import argparse
import re


def trufflehogv2_output(y):
    output = {}
    for i in y["patterns"]:
        if i["pattern"]["confidence"] != "high":
            continue
        output.update({i["pattern"]["name"]: i["pattern"]["regex"]})
    
    return json.dumps(output, indent=4, sort_keys=True)
    

def trufflehogv3_output(y):
    output = []
    for i in y["patterns"]:
        each_name = i["pattern"]["name"]
        each_regex = i["pattern"]["regex"]
        # each_confidence = i["pattern"]["confidence"]

        keywords_list = re.sub(r'[.,;:?!_\-]', ' ', each_name).split()
        output.append({'name': each_name, 'keywords': list(keywords_list),
                      'regex': {each_name: each_regex}})

    return output


def gitleaks_output(y):
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
    return s


def main(arg):
    f = open(arg.database_file, "r")
    y = yaml.safe_load(f.read())
    f.close()
    
    output_string = ""
    ext_string = ""
    if arg.output_type == "trufflehogv2":
        output_string = trufflehogv2_output(y)
        ext_string = "json"
    elif arg.output_type == "gitleaks":
        output_string = gitleaks_output(y)
        ext_string = "toml"
    elif arg.output_type == "trufflehogv3":
        output_string = yaml.dump(trufflehogv3_output(y), sort_keys=False)
        ext_string = "yml"
    
    if arg.export_filename is not None:              
        f = open(f"{arg.export_filename}.{ext_string}", "w")
        if arg.output_type == "trufflehogv3" :
            f.write('detectors:\n')
        f.write(output_string)
        f.close()
    else:
        print(output_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert yaml database file to rules for trufflehogv2, trufflehogv3 or gitleaks')
    parser.add_argument("--db", dest = "database_file", required = True, help = "The yaml database file")
    parser.add_argument("--type", dest= "output_type", required = True, choices=['trufflehogv2', 'trufflehogv3', 'gitleaks'], help = "Supported output types: trufflehog, gitleaks")
    parser.add_argument('--export', dest="export_filename", help = "Give filename, extension toml/json/yaml will be added")
    args = parser.parse_args()
    
    main(args)
