import os
import requests
import json
import subprocess


output_dir = "dev"
proxy_list = 'proxy_list.txt'
exclude_proxy_list = 'exclude_proxy_list.txt'
reject_list = 'reject_list.txt'
geosite_cn = 'geosite_cn.txt'
geoip_cn = 'geoip_cn.txt'
custom_exclude_list = 'custom_exclude_list.txt'
meta_rules = 'geosite-at-cn.txt'


def read_urls_from_file(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        return lines


def merge_json(file):
    data = []
    # 初始化结果字典
    result = {
        "version": 1,
        "rules": {}
    }

    urls = read_urls_from_file(file)
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            data.append(response.json())
    # 遍历数据
    for content in data:
        # 确保每个数据项是字典并且包含 'rules'
        if isinstance(content, dict) and 'rules' in content:
            # 遍历 rules
            for rule in content['rules']:
                # 确保每个规则是字典
                if isinstance(rule, dict):
                    for key, values in rule.items():
                        # 确保值是列表
                        if isinstance(values, list):
                            print(values)
                            result["rules"].setdefault(key, set()).update(values)
                            # 去重并排序
                            # unique_values = sorted(set(values))
                            # 只有当 unique_values 不为空时才添加到结果中
                            # if unique_values:
                            #    result["rules"].setdefault(key, set()).update(unique_values)
    
    # 将集合转换为排序后的列表
    for key in result["rules"]:
        result["rules"][key] = sorted(result["rules"][key])
    
    filepath = os.path.join(output_dir, file.split('.')[0] + ".json")
    with open(filepath, 'w') as f:
        f.write(json.dumps(result, indent=4))
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
    e = merge_json(meta_rules)
    convert_json_to_srs(e)


if __name__ == "__main__":
    main()
