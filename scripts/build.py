import os
import json
import glob
import re
import urllib.request
import time

RULES_DIR = 'rules'
OUTPUT_DIR = 'output'
README_URL = "https://raw.githubusercontent.com/SukkaW/Surge/master/README.md"
# Base URL for the raw JSON files on independent implementation (if available) or constructed from ruleset.skk.moe
# Actually Sukka provides the sing-box versions directly at ruleset.skk.moe/sing-box/...
# We need to map the "Surge" or "Clash" URLs found in README to "sing-box" URLs.
# README typically has links like: https://ruleset.skk.moe/List/domainset/reject.conf
# or https://ruleset.skk.moe/Clash/domainset/reject.txt
#
# The sing-box equivalent is usually:
# https://ruleset.skk.moe/sing-box/domainset/reject.json
# https://ruleset.skk.moe/sing-box/non_ip/reject.json
#
# So we need to:
# 1. Scrape the README for all `ruleset.skk.moe` links.
# 2. Extract the basename (e.g. `reject`).
# 3. Guess the type (domainset, non_ip, ip).
# 4. Construct the sing-box URL.
# 5. Download it.

def parse_rule_file(filepath):
    # (Same as before)
    domain = []
    domain_suffix = []
    ip_cidr = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '/' in line and line.replace('.', '').replace('/', '').isdigit():
                 ip_cidr.append(line)
            else:
                domain_suffix.append(line)
    
    rule_set = {
        "version": 1,
        "rules": [
            {}
        ]
    }
    
    criteria = {}
    if domain:
        criteria['domain'] = domain
    if domain_suffix:
        criteria['domain_suffix'] = domain_suffix
    if ip_cidr:
        criteria['ip_cidr'] = ip_cidr
        
    if not criteria:
        return None

    rule_set['rules'][0] = criteria
    return rule_set

def scrape_and_fetch_external_rules():
    print(f"Fetching README from {README_URL}...")
    try:
        with urllib.request.urlopen(README_URL) as response:
            content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch README: {e}")
        return

    # Find unique rule names and types
    # Look for links like https://ruleset.skk.moe/...
    # Regex to capture the path part
    links = re.findall(r'https://ruleset\.skk\.moe/([a-zA-Z0-9_/-]+\.(?:conf|txt))', content)
    
    # We want to deduplicate based on the resulting sing-box URL.
    # We map found paths to (category, name)
    # Categories in sing-box repo: 'domainset', 'non_ip', 'ip'
    
    targets = set()

    for link in links:
        # link example: List/domainset/reject.conf or Clash/non_ip/reject.txt
        parts = link.split('/')
        if len(parts) < 3:
            continue
            
        # parts[-1] is filename (reject.conf)
        # parts[-2] is category (domainset)
        
        filename = parts[-1]
        name = os.path.splitext(filename)[0] # reject
        category = parts[-2] # domainset, non_ip, ip
        
        # Sukka's categories in URL map pretty well to sing-box categories
        if category not in ['domainset', 'non_ip', 'ip']:
            continue
            
        targets.add((category, name))

    print(f"Found {len(targets)} unique rulesets to mirror.")
    
    for category, name in targets:
        # Construct sing-box URL
        # https://ruleset.skk.moe/sing-box/domainset/reject.json
        sbox_url = f"https://ruleset.skk.moe/sing-box/{category}/{name}.json"
        output_name = f"sukka_{name}_{category}" # e.g. sukka_reject_domainset
        
        output_path = os.path.join(OUTPUT_DIR, f"{output_name}.json")
        
        print(f"Downloading {output_name} from {sbox_url}...")
        try:
            with urllib.request.urlopen(sbox_url) as response:
                data = response.read()
                # Verify JSON
                json.loads(data)
                
                with open(output_path, 'wb') as f:
                    f.write(data)
                print(f"Saved {output_path}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"Skipping {output_name} (Not found for sing-box format)")
            else:
                print(f"Failed {output_name}: {e}")
        except Exception as e:
            print(f"Failed {output_name}: {e}")
            
        time.sleep(0.1) # Be nice to the server

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Process local text files
    for txt_file in glob.glob(os.path.join(RULES_DIR, '*.txt')):
        filename = os.path.basename(txt_file)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"Processing local file {filename}...")
        rule_set = parse_rule_file(txt_file)
        
        if rule_set:
            output_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rule_set, f, indent=2)
            print(f"Generated {output_path}")
            
    # Fetch external rules dynamically
    scrape_and_fetch_external_rules()

if __name__ == '__main__':
    main()
