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
db_file = 'geosite.db'



def read_urls_from_file(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        return lines



def get_category_file(categories):    
    for category in categories:
        flags = ""
        os.system("sing-box geosite export --output " + output_dir + "/" + category + ".json " + category)
        # print(os.path.getsize(db_file))



def merge_json_files_in_folder(folder_path):
    merged_data = {
        "version": 1,
        "rules": []
    }

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for rule in data.get('rules', []):
                    # 查找现有规则以合并
                    existing_rule = next(
                        (r for r in merged_data['rules'] if r['domain'] == rule['domain']),
                        None
                    )
                    if existing_rule:
                        # 分别合并 'domain_suffix', 'domain_keyword', 'domain_regex'
                        for key in ['domain_suffix', 'domain_keyword', 'domain_regex']:
                            if key in rule and isinstance(rule[key], list):
                                if key in existing_rule:
                                    existing_rule[key].extend(rule[key])
                                else:
                                    existing_rule[key] = rule[key]
                    else:
                        # 添加新规则
                        merged_data['rules'].append(rule)

    return merged_data



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
            data.append(json.loads(response.text))
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
                            # 去重并排序
                            unique_values = sorted(set(values))
                            # 只有当 unique_values 不为空时才添加到结果中
                            if unique_values:
                                result["rules"].setdefault(key, set()).update(unique_values)
    
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
    categories = ["firebase@cn", "ubisoft@cn", "microsoft-pki@cn", "google-play@cn", "okaapps@cn", "thelinuxfoundation@cn", "amp@cn", "amd@cn", "kechuang@cn", "openjsfoundation@cn", "thetype@cn", "category-cryptocurrency@cn", "adobe@cn", "category-finance@cn", "muji@cn", "duolingo@cn", "asus@cn", "mapbox@cn", "bluearchive@cn", "aerogard@cn", "oreilly@cn", "test-ipv6@cn", "airwick@cn", "walmart@cn", "xbox@cn", "adidas@cn", "teamviewer@cn", "dell@cn", "pearson@cn", "starbucks@cn", "familymart@cn", "st@cn", "westerndigital@cn", "booking@cn", "reabble@cn", "fflogs@cn", "bluepoch-games@cn", "okx@cn", "mortein@cn", "acer@cn", "panasonic@cn", "movefree@cn", "epicgames@cn", "category-remote-control@cn", "gucci@cn", "hm@cn", "category-tech-media@cn", "calgoncarbon@cn", "youtube@cn", "hp@cn", "tvb@cn", "samsung@cn", "vanish@cn", "ifast@cn", "sslcom@cn", "tencent-dev@cn", "dettol@cn", "webex@cn", "vmware@cn", "bytedance@cn", "yahoo@cn", "shopee@cn", "finish@cn", "att@cn", "canon@cn", "jetbrains@cn", "swift@cn", "linkedin@cn", "verizon@cn", "clearasil@cn", "digicert@cn", "lysol@cn", "strepsils@cn", "kurogames@cn", "veet@cn", "meadjohnson@cn", "riot@cn", "bluepoch@cn", "woolite@cn", "category-social-media-!cn@cn", "msn@cn", "hketgroup@cn", "primevideo@cn", "nurofen@cn", "gigabyte@cn", "durex@cn", "razer@cn", "mcdonalds@cn", "farfetch@cn", "kindle@cn", "bestbuy@cn", "nvidia@cn", "miniso@cn", "bridgestone@cn", "qnap@cn", "intel@cn", "microsoft-dev@cn", "bmw@cn", "google-trust-services@cn", "cisco@cn", "apple-pki@cn", "category-media@cn", "apple-dev@cn", "ikea@cn", "tesla@cn", "gog@cn", "itunes@cn", "sectigo@cn", "category-enhance-gaming@cn", "globalsign@cn", "category-ntp-cn@cn", "icloud@cn", "mastercard@cn", "qualcomm@cn", "bilibili-game@cn", "bilibili@cn", "category-ntp@cn", "volvo@cn", "bing@cn", "beats@cn", "visa@cn", "akamai@cn", "category-dev@cn", "nintendo@cn", "paypal@cn", "mihoyo@cn", "mihoyo-cn@cn", "steam@cn", "cloudflare@cn", "cloudflare-cn@cn", "nike@cn", "category-entertainment-cn@cn", "aws@cn", "aws-cn@cn", "huawei-dev@cn", "huawei@cn", "category-cas@cn", "category-dev-cn@cn", "rb@cn", "ebay@cn", "amazon@cn", "azure@cn", "category-ecommerce@cn", "tencent-games@cn", "tencent@cn", "google@cn", "microsoft@cn", "category-games@cn", "category-entertainment@cn", "apple@cn", "geolocation-cn@cn", "category-companies@cn"]

    
    # print("1:" + os.getcwd())
    # testpath = os.path.join(os.getcwd(), branch_name, file_name)
    # print("2:" + testpath)
    # with open(file_name, 'r') as f:
    #     lines = f.read().splitlines()
    #     print("3:" + lines)
    print(db_file)
    if os.path.isfile(db_file):
        size = os.path.getsize(db_file)
        print(size)
        
    
    get_category_file(categories)
    

    # 假设hidden文件夹位于当前工作目录下
    merged_json_data = merge_json_files_in_folder(output_dir)
    print(merged_json_data)


    # e = merge_json(meta_rules)
    # convert_json_to_srs(e)


if __name__ == "__main__":
    main()
