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
meta_rules = 'geosite@cn.txt'


def read_urls_from_file(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        return lines


def merge_json(file):
    # 定义需要处理的键
    required_keys = ['domain', 'domain_suffix', 'domain_keyword', 'domain_regex']
    
    # 初始化字典以存储唯一值
    unique_rules = {key: set() for key in required_keys}
    
    # 文件列表
    urls = read_urls_from_file(file)
    
    
    # 处理每个文件
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # 确保请求成功
            data = json.loads(response.text)
            
                
            # 检查并匹配四个键
            for key in required_keys:
                if key in data:
                    unique_rules[key].update(data[key])
        except FileNotFoundError:
            print(f"File {file_name} not found.")
        except json.JSONDecodeError:
            print(f"File {file_name} is not a valid JSON.")
    print(unique_rules)
    # 将集合转换回列表，并进行排序
    for key in unique_rules:
        unique_rules[key] = sorted(list(unique_rules[key]))
    
    result = {
        "version": 1,
        "rules": unique_rules
    }
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
