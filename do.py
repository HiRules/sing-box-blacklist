import os
import requests
import json
import subprocess


files = []
output_dir = "release"
blacklist = 'blacklist.txt'
excludelist = 'excludelist.txt'
blocklist = 'blocklist.txt'
geosite_cn = 'geosite_cn.txt'
geoip_cn = 'geoip_cn.txt'
custom_excludelist = 'custom_excludelist.txt'


def read_urls_from_file(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        return lines


def read_domain_from_excludelist(file):
    try:
        with open(file, 'r') as f:
            lines = f.read().splitlines()
            return lines
    except FileNotFoundError:
        print(f"File not found: {excludelist}")
        return []


def fetch_and_deduplicate_content(urls):
    result = set()
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    e = line.strip()
                    if e:
                        result.add(e)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    result = list(result)
    result.sort()
    return result


def fetch_and_deduplicate_cn_domain(urls):
    result = set()
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    if not line.startswith("#"):
                        domain = re.match(r"server=\/(.*)\/(.*)", line)
                        if domain:
                            result.add(domain.group(1))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    result = list(result)
    result.sort()
    return result


def process_and_filter_content(content_list, domain_list):
    new_list = []
    for content in content_list:
        if not any(content.startswith(domain) for domain in domain_list):
            new_list.append(content)
    return new_list


def json_of_domain(new_list, file):
    data = []
    domain = []
    domain_suffix = []
    domain_keyword = []
    for item in new_list:
        if item.startswith('.'):
            domain_suffix.append(item)
        elif item.count('.') > 0:
            domain.append(item)
        else:
            domain_keyword.append(item)
    if domain:
        data.append({"domain": domain})
    if domain_suffix:
        data.append({"domain_suffix": domain_suffix})
    if domain_keyword:
        data.append({"domain_keyword": domain_keyword})
    result = {
        "version": 1,
        "rules": data
    }
    filepath = os.path.join(output_dir, file.split('.')[0] + ".json")
    with open(filepath, 'w') as f:
        f.write(json.dumps(result, indent=4))
        print(f"Successfully generated JSON file {filepath}.")
    return filepath


def json_of_ip(new_list, file):
    data = []
    ip_cidr = []
    for item in new_list:
        if not item.startswith("#"):
            ip_cidr.append(item)
    if ip_cidr:
        data.append({"ip_cidr": ip_cidr})
    result = {
        "version": 1,
        "rules": data
    }
    filepath = os.path.join(output_dir, file.split('.')[0] + ".json")
    with open(filepath, 'w') as f:
        f.write(json.dumps(result, indent=4))
        print(f"Successfully generated JSON file {filepath}.")
    return filepath


def convert_json_to_srs(json_file):
    srs_file = json_file.replace(".json", ".srs")
    try:
        os.system("sing-box rule-set compile --output " + srs_file + " " + json_file)
        return json_file, srs_file
        print(f"Successfully converted JSON to {srs_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting JSON to SRS: {e}")


def result_of_gfw_domain(lists, ce):
    for list in lists:
        e = read_urls_from_file(list)
        e = fetch_and_deduplicate_content(e)
        e = process_and_filter_content(e, read_domain_from_excludelist(ce))
        e = json_of_domain(e, list)
        e = convert_json_to_srs(e)
    return e


def result_of_cn_domain(list):
    e = read_urls_from_file(list)
    e = fetch_and_deduplicate_cn_domain(e)
    e = json_of_domain(e, list)
    e = convert_json_to_srs(e)
    return e


def result_of_ip(list):
    e = read_urls_from_file(list)
    e = fetch_and_deduplicate_content(e)
    e = json_of_ip(e, list)
    e = convert_json_to_srs(e)
    return e


def main():
    os.mkdir(output_dir)
    subprocess.run(['git', 'checkout', 'hidden'], check=True)
    files = [blacklist, excludelist, blocklist]
    result_of_gfw_domain(files, custom_excludelist)
    result_of_cn_domain(geosite_cn)
    result_of_ip(geoip_cn)


if __name__ == "__main__":
    main()
