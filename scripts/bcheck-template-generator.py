import yaml
import requests
import os

bcheck_templates = {}

def download_rules(url):
    response = requests.get(url)
    if response.status_code == 200:
        return yaml.safe_load(response.text)
    else:
        raise Exception("Failed to download rules")

def create_bcheck_template(name, regex, severity):
    bcheck_templates[str(severity)] = f"""metadata:
 language: v1-beta
 name: "Information Disclosure"
 description: "Detects secret patterns in responses."
 author: "bugswagger team, xelkomy, juba0x00"
 tags: "secret, bugswagger"

given response then
 if {{latest.response}} matches "bugswagger" then
      report issue:
        severity: low
        confidence: firm
        detail: "bugswagger secret pattern detected in the response."
        remediation: "Review and remove unnecessary exposure of secrets."

"""
    
def append_condition(name: str, severity: str, regex: str)-> None:
    value = f"""
 else if {{latest.response}} matches "{regex}" then
      report issue:
        severity: {severity}
        confidence: firm
        detail: "{name} secret pattern detected in the response."
        remediation: "Review and remove unnecessary exposure of secrets."
"""
    bcheck_templates[severity] += value

def save_bcheck_file(name, content):
    filename = f"{name.replace(' ', '_').lower()}.bcheck"
    with open(filename, 'w') as file:
        file.write(content)

def main():
    url = "https://raw.githubusercontent.com/mazen160/secrets-patterns-db/master/db/rules-stable.yml"
    rules = download_rules(url)

    if not os.path.exists('bcheckskeys'):
        os.makedirs('bcheckskeys')
    os.chdir('bcheckskeys')

    patterns = rules['patterns']
    for pattern in patterns:
        name = pattern.get('pattern').get('name')
        regex = pattern.get('pattern').get('regex').replace('"', '\\"')
        severity = pattern.get('pattern').get('confidence')
        if name and regex and severity:
            if severity in bcheck_templates.keys():
                append_condition(name, severity, regex)
            else:
                create_bcheck_template(name, regex, severity)
    
    for key, value in bcheck_templates.items():
        value += "  end if"
        print(f'saving {key}.bcheck')
        save_bcheck_file(key, value)
    
if __name__ == "__main__":
    main()
