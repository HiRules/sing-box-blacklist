import os
import requests
import json
import subprocess
from collections import defaultdict


output_dir = "dev"
proxy_list = 'proxy_list.txt'
exclude_proxy_list = 'exclude_proxy_list.txt'
reject_list = 'reject_list.txt'
geosite_cn = 'geosite_cn.txt'
geoip_cn = 'geoip_cn.txt'
custom_exclude_list = 'custom_exclude_list.txt'
meta_rules = 'geosite@cn.txt'


def read_urls_from_file(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        return lines


def merge_json(file):
    # 初始化结果字典
    result = {
        "version": 1,
        "rules": {}
    }
    
    # 遍历模拟数据
    for data in read_urls_from_file(file):
        # 遍历 rules
        rules = data.get("rules") or []
        for rule in rules:
            for key, values in rule.items():
                if values:  # 只处理非空值
                    if key in result["rules"]:
                        result["rules"][key].update(values)
                    else:
                        result["rules"][key] = set(values)
    
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
