import os
import requests
import json

output_dir = "./release"


files = []

# 获取文件名
def pull_filename(url):
    filename = os.path.basename(url)
    filename = os.path.splitext(filename)[0]
    return filename

# 读取文本文件，返回 URL 列表
def read_urls_from_file(filepath):
    with open(filepath, 'r') as file:
        urls = file.read().splitlines()
    return urls

# 获取 URL 内容，并返回去重结果
def fetch_and_deduplicate_content(urls):
    content_set = set()
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.text.splitlines()
                for line in lines:
                    e = line.strip()
                    if e:
                        content_set.add(e)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    content_set = list(content_set)
    content_set.sort()
    return content_set

# 处理去重内容，并与域名对比
def process_and_filter_content(content_list, domain_list):
    new_list = []
    for content in content_list:
        if not any(content.startswith(domain) for domain in domain_list):
            new_list.append(content)
    return new_list


# 新的 json 文件生成
def classify_content(new_list, url):
    data = []
    domain = []
    domain_suffix = []
    for item in new_list:
        if item.startswith('.'):
            domain_suffix.append(item)
        else:
            domain.append(item)
    if domain:
        data.append({"domain": domain})
    if domain_suffix:
        data.append({"domain_suffix": domain_suffix})
    result = {
        "version": 1,
        "rules": data
    }
    filepath = os.path.join(output_dir, pull_filename(url) + ".json")
    with open(filepath, 'w') as f:
        f.write(json.dumps(result, indent=4))
        print(f"Successfully generated JSON file {filepath}.")
    return filepath

# 使用sing-box将JSON转换为.srs格式
def convert_json_to_srs(json_file):
    srs_file = json_file.replace(".json", ".srs")
    try:
        os.system("sing-box rule-set compile --output " + srs_file + " " + json_file)
        return json_file, srs_file
        print(f"Successfully converted JSON to {srs_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting JSON to SRS: {e}")

def result(lists, ce):

    # 读取域名列表
    with open(ce, 'r') as file:
        ce = file.read().splitlines()
    
    for list in lists:
        e = read_urls_from_file(list)
        e = fetch_and_deduplicate_content(e)
        e = process_and_filter_content(e, ce)
        e = classify_content(e, list)
        e = convert_json_to_srs(e)
    return e


# 主函数
def main():
    os.mkdir(output_dir)

    files = [blacklist, excludelist, blocklist]
    
    result(files, custom_excludelist)

if __name__ == "__main__":
    main()
