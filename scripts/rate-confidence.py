#!/usr/bin/env python3

# This script runs every rule against top websites and files from top github repos
# Rules with higher hit rates are assigned lower confidence scores
# Final YAML with confidence scores is printed at the end.

import re
import sys
import yaml
import random
import subprocess
from math import ceil
from hashlib import md5
from pathlib import Path
from contextlib import suppress
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# how many of the top websites to visit
num_websites = 2000
# how many files to check in a single batch
batch_size = 100
# skip these files
file_ext_blacklist = (".png", ".jpg", ".bmp", ".ico", ".jpeg", ".gif", ".svg", ".css", ".woff", ".woff2", ".ttf", ".mp3", ".m4a", ".wav", ".flac", ".mp4", ".mkv", ".avi", ".wmv", ".mov", ".flv", ".webm")

project_root = Path(__file__).resolve().parent.parent
temp_dir = Path.home() / ".cache" / "secret-patterns-db"
temp_dir.mkdir(exist_ok=True)

files = []

def errprint(*args, **kwargs):
    kwargs["file"] = sys.stderr
    kwargs["flush"] = True
    print(*args, **kwargs)


def hash_file(file):
    with open(file, 'rb') as f:
        content = f.read()
        return md5(content).digest()


### PARSE TEMPLATES ###

errprint(f"Parsing templates")
rules = {}
template_file = Path(__file__).resolve().parent.parent / "db" / "rules-stable.yml"
with open(template_file) as f:
    rules_yaml = yaml.safe_load(f).get("patterns", [])
for r in rules_yaml:
    r = r.get("pattern", {})
    if not r:
        continue
    name = r.get("name", "")
    if name:
        regex = r.get("regex", "")
        try:
            compiled_regex = re.compile(regex)
            r["compiled_regex"] = compiled_regex
            rules[name] = r
        except Exception:
            pass

### VISIT WEBSITES ###

errprint(f"Visiting websites")
top_domains_file = project_root / "datasets" / "top-1m-alexa-domains.csv"
with open(top_domains_file) as f:
    top_domains = [l.split(",")[-1] for l in f.read().splitlines()[:num_websites]]
websites_dir = temp_dir / "websites"
websites_dir.mkdir(exist_ok=True)

def get_webpage(url):
    command = ["wget", "-q", "--convert-links", "--adjust-extension", "--page-requisites", "--no-parent", "--header=User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", url]
    with suppress(subprocess.TimeoutExpired):
        subprocess.run(command, cwd=websites_dir, timeout=10)

# with ThreadPoolExecutor(max_workers=25) as e:
#     for domain in top_domains[:num_websites]:
#         e.submit(get_webpage, f"https://{domain}")

# get all files
files = list(websites_dir.glob("**/*"))
# filter out unwanted ones
files = [f for f in files if f.is_file() and f.suffix.lower() not in file_ext_blacklist]
# dedupe
files_before = len(files)
errprint(f"Deduplicating {len(files):,} files")
file_hashes = {hash_file(f): f for f in files}
files = list(file_hashes.values())
files_after = len(files)
errprint(f"Deduplicated {files_before:,} --> {files_after:,}")
# shuffle
random.shuffle(files)
if not files:
    errprint(f"No websites loaded")
    exit(1)

def split(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i:i + chunk_size]

def test_batch(regex, *files):
    matches = 0
    for file in files:
        with open(file, errors='ignore') as f:
            content = f.read()
        if not content:
            continue
        if regex.search(content):
            matches += 1
    return matches

### BEGIN TESTING RULES ###

errprint(f"Testing {len(rules):,} rules against {len(files):,} files")
futures = dict()
total_checks = max(1, len(files) * len(rules))
batch_size = min(len(files), batch_size)
with ProcessPoolExecutor() as e:
    for file_batch in split(files, batch_size):
        for name, r in rules.items():
            # print(len(file_batch))
            regex = r["compiled_regex"]
            future = e.submit(test_batch, regex, *file_batch)
            futures[future] = name

    signatures = dict()

    try:
        for i, f in enumerate(as_completed(futures)):
            completed = i*batch_size
            percent = completed / total_checks * 100
            errprint(f"\rCompleted {completed:,} rule checks ({percent:.1f}%)", end="")
            name = futures[f]
            result = f.result()
            try:
                signatures[name] += result
            except KeyError:
                signatures[name] = result
    except KeyboardInterrupt:
        e.shutdown(cancel_futures=True)
        pass

    new_rules_yaml = {"patterns": []}
    bad_sigs = {k:v for k,v in signatures.items() if v > 0}
    avg_badness = sum(bad_sigs.values()) / max(1, len(bad_sigs))
    for name, hits in sorted(signatures.items(), key=lambda x: x[-1], reverse=True):
        if hits > 0:
            confidence = min(100, max(0, 100 - ceil(hits / avg_badness * 100)))
        else:
            confidence = 100
        rule = rules[name]
        yaml_rule = {
            "pattern": {
                "name": name,
                "regex": rule["regex"],
                "confidence": confidence
            }
        }
        new_rules_yaml["patterns"].append(yaml_rule)

    new_rules_yaml["patterns"].sort(key=lambda x: x["pattern"]["name"])

    # print final YAML
    print(yaml.safe_dump(new_rules_yaml))
