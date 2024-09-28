import os
import requests
import re
import json
import subprocess


output_dir = "release"
proxy_list = 'proxy_list.txt'
exclude_proxy_list = 'exclude_proxy_list.txt'
reject_list = 'reject_list.txt'
geosite_cn = 'geosite_cn.txt'
geoip_cn = 'geoip_cn.txt'
custom_exclude_list = 'custom_exclude_list.txt'


def read_urls_from_file(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        return lines


def fffremove_matching_rows(a, b):
    new_a = []
    b = list(b)
    for row_a in a:
        if row_a not in b:
            new_a.append(row_a)
    print(new_a)
    return new_a


def remove_matching_rows(a, b):
    return [line for line in a if line not in b]


def json_of_proxy_list(file, cel):
    merged_file = set()
    excluded_file = []
    data = []
    domain = []
    domain_suffix = []
    domain_keyword = []
    with open(file, 'r') as f:
        urls = f.read().splitlines()
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            lines = response.text.splitlines()
            for line in lines:
                e = line.strip()
                if e:
                    merged_file.add(e)
    merged_file = list(merged_file)
    merged_file.sort()
    excluded_file = remove_matching_rows(merged_file, cel)
    for line in excluded_file:
        if line.startswith('.'):
            domain_suffix.append(line)
            domain.append(line.lstrip('.'))
        elif line.count('.') > 0:
            domain.append(line)
        else:
            domain_keyword.append(line)
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


def fetch_and_deduplicate_content(urls):
    result = set()
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            lines = response.text.splitlines()
            for line in lines:
                e = line.strip()
                if e:
                    result.add(e)
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
                    if line.strip() != '' and not line.startswith('#'):
                        domain = re.match(r"server=\/(.*)\/(.*)", line)
                        domain = domain.group(1)
                        if domain:
                            result.add(domain)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    result = list(result)
    result.sort()
    return result


def json_of_cn_domain(new_list, file):
    data = []
    domain = []
    domain_suffix = []
    domain_keyword = []
    for line in new_list:
        if line.count('.') > 0:
            domain.append(line)
            domain_suffix.append('.' + line)
        else:
            domain_suffix.append('.' + line)
    if domain:
        data.append({"domain": domain})
    if domain_suffix:
        data.append({"domain_suffix": domain_suffix})
    result = {
        "version": 1,
        "rules": data
    }
    filepath = os.path.join(output_dir, file.split('.')[0] + ".json")
    with open(filepath, 'w') as f:
        f.write(json.dumps(result, indent=4))
        print(f"Successfully generated JSON file {filepath}.")
    return filepath


def json_of_domain(new_list, file):
    data = []
    domain = []
    domain_suffix = []
    domain_keyword = []
    for line in new_list:
        if line.startswith('.'):
            domain_suffix.append(line)
            domain.append(line.lstrip('.'))
        elif line.count('.') > 0:
            domain.append(line)
        else:
            domain_keyword.append(line)
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


def result_of_gfw_domain(file, cel):
    e = json_of_proxy_list(file, cel)
    e = convert_json_to_srs(e)
    return e


def result_of_exclude_proxy_domain(file):
    e = read_urls_from_file(file)
    e = fetch_and_deduplicate_content(e)
    e = json_of_domain(e, file)
    e = convert_json_to_srs(e)
    return e


def result_of_reject_domain(file):
    e = read_urls_from_file(file)
    e = fetch_and_deduplicate_content(e)
    e = json_of_domain(e, file)
    e = convert_json_to_srs(e)
    return e


def result_of_cn_domain(file):
    e = read_urls_from_file(file)
    e = fetch_and_deduplicate_cn_domain(e)
    e = json_of_cn_domain(e, file)
    e = convert_json_to_srs(e)
    return e


def result_of_ip(file):
    e = read_urls_from_file(file)
    e = fetch_and_deduplicate_content(e)
    e = json_of_ip(e, file)
    e = convert_json_to_srs(e)
    return e


def main():
    os.mkdir(output_dir)
    subprocess.run(['git', 'checkout', 'hidden'], check=True)
    result_of_gfw_domain(proxy_list, custom_exclude_list)
    #result_of_exclude_proxy_domain(exclude_proxy_list)
    result_of_reject_domain(reject_list)
    result_of_cn_domain(geosite_cn)
    result_of_ip(geoip_cn)


if __name__ == "__main__":
    main()
