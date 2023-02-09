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
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# how many of the top git repos to clone
num_repos = 20
# how many random file samples to take from each repo
files_per_repo = 500
# how many of the top websites to visit
num_websites = 1000
# how many files to check in a single batch
batch_size = 100

project_root = Path(__file__).resolve().parent.parent
temp_dir = Path.home() / ".cache" / "secret-patterns-db"
temp_dir.mkdir(exist_ok=True)

files = []

def errprint(*args, **kwargs):
    kwargs["file"] = sys.stderr
    kwargs["flush"] = True
    print(*args, **kwargs)

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
    name = r.get("name", "").lower()
    confidence = r.get("confidence", "").lower()
    if name and confidence:
        regex = r.get("regex", "")
        try:
            compiled_regex = re.compile(regex)
            r["compiled_regex"] = compiled_regex
            rules[name] = r
        except Exception:
            pass

### VISIT WEBSITES ###

errprint(f"Visiting websites")
top_websites_file = project_root / "datasets" / "top-websites.txt"
top_websites = open(top_websites_file).read().splitlines()
websites_dir = temp_dir / "websites"
websites_dir.mkdir(exist_ok=True)

with ThreadPoolExecutor(max_workers=25) as e:
    for url in top_websites[:num_websites]:
        domain = url.split("/")[2]
        output_file = websites_dir / f"{domain}.txt"
        command = ["curl", "--connect-timeout", "10", "--max-time", "10", "-s", "-L", "-i", "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", "-o", output_file, url]
        if not output_file.is_file():
            e.submit(subprocess.run, command, cwd=websites_dir)

files = list(websites_dir.glob("*"))

### CLONE REPOS ###

top_github_repos_file = project_root / "datasets" / "top-github-repos.txt"
top_github_repos = open(top_github_repos_file).read().splitlines()
git_repos_dir = temp_dir / "git"
git_repos_dir.mkdir(exist_ok=True)

top_github_repos = [(git_repos_dir / (r.split("/")[-2] + "-" + r.split("/")[-1]), r) for r in top_github_repos]

errprint(f"Cloning git repos")
with ThreadPoolExecutor(max_workers=5) as e:
    for repo_dir, repo in list(set(top_github_repos[:num_repos])):
        command = ["git", "clone", "--depth", "1", "--filter=blob:limit=1m", repo, repo_dir.name]
        if not repo_dir.is_dir():
            e.submit(subprocess.run, command, cwd=git_repos_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

for repo_dir, repo in top_github_repos:
    if not repo_dir.is_dir():
        continue
    repo_files = repo_dir.glob("**/*")
    # files only
    repo_files = [f for f in repo_files if f.is_file()]
    # not git database
    repo_files = [f for f in repo_files if not str(f.relative_to(git_repos_dir)).split('/')[1] == ".git"]
    # files 1MB or less in size
    repo_files = [f for f in repo_files if 0 < f.stat().st_size < 10**6]
    errprint(f"Found {len(repo_files):,} files in {repo_dir}")
    random.shuffle(repo_files)
    files += repo_files[:files_per_repo]


random.shuffle(files)

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
total_checks = len(files) * len(rules)
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
