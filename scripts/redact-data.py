import yaml
import sys
import re
import time
REDACTION = "[REDACTED - ({name})]"

with open(sys.argv[1], "r") as f:
    RULES = yaml.safe_load(f)
with open(sys.argv[2], "rb", ) as f:
    DATA = f.read().decode("utf-8", "ignore")

for i in RULES["patterns"]:
    pattern = i["pattern"]
    name = pattern.get('name')
    regex = pattern.get('regex')
    confidence = pattern.get('confidence')
    if confidence != "high":
        continue
    start_time = time.time()

    result_string = DATA
    try:
        result_string = re.sub(regex, REDACTION.replace("{name}", name), DATA)
    except Exception as e:
        print(e)
        print(f"EXCEPTION: *** Name: {name}")

    if result_string != DATA:
        print(f"*** Data updated. Rule: {name}")
        DATA = result_string

    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Name: {name}\t Confidence: {confidence}\t Regex: {regex}\n\n")
    print(f"Execution time: {execution_time} seconds")
    print("*" * 50)


# print(f"# NEW DATA:\n\n\n{DATA}")

with open("redacted-output.txt", "w") as f:
    f.write(DATA)
