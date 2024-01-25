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

def create_bcheck_template(name, regex, confidence):
    bcheck_templates[str(confidence)] = f"""metadata:
 language: v1-beta
 name: "Information Disclosure Secret Finder - {confidence}"
 description: "Detects secret patterns in responses."
 author: "bugswagger, xelkomy, juba0x00, xhzeem"
 tags: "secret, bugswagger"

given response then
"""
    
def append_condition(name: str, confidence: str, regex: str)-> None:
    value = f"""
 if {{latest.response}} matches "{regex}" then
      report issue:
        severity: medium
        confidence: {confidence}
        detail: "{name} secret pattern detected in the response."
        remediation: "Review and remove unnecessary exposure of secrets."
 end if
"""
    bcheck_templates[confidence] += value

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
        regex = pattern['pattern']['regex'].replace(r'\"','"').replace('"', r'\"')
        name = pattern['pattern']['name']
        confidence = pattern['pattern']['confidence'].lower()

        # Replace confidence levels
        if confidence == 'high':
            confidence = 'certain'
        elif confidence == 'medium':
            confidence = 'firm'
        elif confidence == 'low':
            confidence = 'tentative'

        if name and regex and confidence:
            if confidence in bcheck_templates.keys():
                append_condition(name, confidence, regex)
            else:
                create_bcheck_template(name, regex, confidence)
    
    for key, value in bcheck_templates.items():
        print(f'saving {key}.bcheck')
        save_bcheck_file(key, value)
    
if __name__ == "__main__":
    main()
