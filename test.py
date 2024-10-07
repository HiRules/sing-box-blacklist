import os
import requests
import json
import subprocess


source_dir = "dev001"
output_dir = "dev002"
output_file = "cn.json"
proxy_list = 'proxy_list.txt'
exclude_proxy_list = 'exclude_proxy_list.txt'
reject_list = 'reject_list.txt'
geosite_cn = 'geosite_cn.txt'
geoip_cn = 'geoip_cn.txt'
custom_exclude_list = 'custom_exclude_list.txt'
db_file = 'adobe@cn.json'
categories = ["tld-cn", "geolocation-cn", "apple-cn", "google-cn", "firebase@cn", "ubisoft@cn", "microsoft-pki@cn", "google-play@cn", "okaapps@cn", "thelinuxfoundation@cn", "amp@cn", "amd@cn", "kechuang@cn", "openjsfoundation@cn", "thetype@cn", "category-cryptocurrency@cn", "adobe@cn", "category-finance@cn", "muji@cn", "duolingo@cn", "asus@cn", "mapbox@cn", "bluearchive@cn", "aerogard@cn", "oreilly@cn", "test-ipv6@cn", "airwick@cn", "walmart@cn", "xbox@cn", "adidas@cn", "teamviewer@cn", "dell@cn", "pearson@cn", "starbucks@cn", "familymart@cn", "st@cn", "westerndigital@cn", "booking@cn", "reabble@cn", "fflogs@cn", "bluepoch-games@cn", "okx@cn", "mortein@cn", "acer@cn", "panasonic@cn", "movefree@cn", "epicgames@cn", "category-remote-control@cn", "gucci@cn", "hm@cn", "category-tech-media@cn", "calgoncarbon@cn", "youtube@cn", "hp@cn", "tvb@cn", "samsung@cn", "vanish@cn", "ifast@cn", "sslcom@cn", "tencent-dev@cn", "dettol@cn", "webex@cn", "vmware@cn", "bytedance@cn", "yahoo@cn", "shopee@cn", "finish@cn", "att@cn", "canon@cn", "jetbrains@cn", "swift@cn", "linkedin@cn", "verizon@cn", "clearasil@cn", "digicert@cn", "lysol@cn", "strepsils@cn", "kurogames@cn", "veet@cn", "meadjohnson@cn", "riot@cn", "bluepoch@cn", "woolite@cn", "category-social-media-!cn@cn", "msn@cn", "hketgroup@cn", "primevideo@cn", "nurofen@cn", "gigabyte@cn", "durex@cn", "razer@cn", "mcdonalds@cn", "farfetch@cn", "kindle@cn", "bestbuy@cn", "nvidia@cn", "miniso@cn", "bridgestone@cn", "qnap@cn", "intel@cn", "microsoft-dev@cn", "bmw@cn", "google-trust-services@cn", "cisco@cn", "apple-pki@cn", "category-media@cn", "apple-dev@cn", "ikea@cn", "tesla@cn", "gog@cn", "itunes@cn", "sectigo@cn", "category-enhance-gaming@cn", "globalsign@cn", "category-ntp-cn@cn", "icloud@cn", "mastercard@cn", "qualcomm@cn", "bilibili-game@cn", "bilibili@cn", "category-ntp@cn", "volvo@cn", "bing@cn", "beats@cn", "visa@cn", "akamai@cn", "category-dev@cn", "nintendo@cn", "paypal@cn", "mihoyo@cn", "mihoyo-cn@cn", "steam@cn", "cloudflare@cn", "cloudflare-cn@cn", "nike@cn", "category-entertainment-cn@cn", "aws@cn", "aws-cn@cn", "huawei-dev@cn", "huawei@cn", "category-cas@cn", "category-dev-cn@cn", "rb@cn", "ebay@cn", "amazon@cn", "azure@cn", "category-ecommerce@cn", "tencent-games@cn", "tencent@cn", "google@cn", "microsoft@cn", "category-games@cn", "category-entertainment@cn", "apple@cn", "geolocation-cn@cn", "category-companies@cn"]
geosite = "https://github.com/MetaCubeX/meta-rules-dat/raw/refs/heads/release/geosite.db"



def read_urls_from_file(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        return lines


def download_file(url, folder_path):
    filename = url.split("/")[-1]
    save_path = os.path.join(folder_path, filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, "wb") as file:
        file.write(response.content)



def get_category_file(source_dir, categories):    
    for category in categories:
        test = os.system("sing-box geosite export -o " + source_dir + "/" + category + ".json " + category)
        print(test)



def merge_json_files(source_dir, output_dir, output_file):
    merged_data = {
        "version": 1,
        "rules": []
    }
    rules_dict = {}

    for filename in os.listdir(source_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(source_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for rule in data['rules']:
                    for key in ['domain', 'domain_suffix', 'domain_keyword', 'domain_regex']:
                        if key in rule:
                            if key not in rules_dict:
                                rules_dict[key] = set()
                            rules_dict[key].update(rule[key] if isinstance(rule[key], list) else [rule[key]])

    for key, values in rules_dict.items():
        merged_data['rules'].append({key: sorted(list(values))})
    
    filepath = os.path.join(output_dir, output_file)
    with open(filepath, 'w') as f:
        f.write(json.dumps(merged_data, indent=4))
    return filepath




def merge_json(file):
    data = []
    result = {
        "version": 1,
        "rules": {}
    }

    urls = read_urls_from_file(file)
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            data.append(json.loads(response.text))
    for content in data:
        if isinstance(content, dict) and 'rules' in content:
            for rule in content['rules']:
                if isinstance(rule, dict):
                    for key, values in rule.items():
                        if isinstance(values, list):
                            unique_values = sorted(set(values))
                            if unique_values:
                                result["rules"].setdefault(key, set()).update(unique_values)
    
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
    os.mkdir(source_dir)
    os.mkdir(output_dir)
    # ingpath = 'test'
    # os.mkdir(ingpath)
    subprocess.run(['git', 'switch', source_dir], check=True)
    # download_file(geosite, ingpath)
    # download_file(geosite, testdir)

    # if os.path.isfile(db_file):
    #     size = os.path.getsize(db_file)
    #     print(size)
    # out = []
    # with open(db_file, 'r') as f:
    #     for line in f:
    #         line = line.strip()
    #         out.append(line)
    #     print(out)
        
    
    get_category_file(source_dir, categories)
    
    merged_json_data = merge_json_files(source_dir, output_dir, output_file)
    print(merged_json_data)


    # e = merge_json(meta_rules)
    # convert_json_to_srs(e)


if __name__ == "__main__":
    main()
