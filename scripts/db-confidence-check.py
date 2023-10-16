import re
import os
import yaml

with open(os.getenv("FILE"), "r") as f:
    FILE = f.read()
    print("File loaded")

with open("../db/pii-stable.yml", "r") as f:
    RULES = yaml.safe_load(f.read())


rules_count = 0
for i in RULES["patterns"]:
    times_repeated = 0
    rules_count += 1
    print(f"Rule number: {rules_count}")

    pattern = i["pattern"]
    if pattern["confidence"] != "high":
        continue
    r = re.compile(pattern["regex"])
    data = r.findall(FILE)
    for j in data:
        print(j)
        with open("results.txt", "a") as f:
            f.write(f"{j}\n\n")
        times_repeated+= 1
    if times_repeated > 0:
        with open("log.txt", "a") as f:
            f.write(f"{pattern['name']}\t{pattern['confidence']}\t{times_repeated}\n")
        print(f"Rule with above threshold matches: {pattern['name']} - {pattern['confidence']}\n")
