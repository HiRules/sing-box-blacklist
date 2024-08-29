import os
import requests
import json

files = []
output_dir = "./release"
b_file = 'blacklist.txt'
e_file = 'excludelist.txt'
domain_file = 'excludecustomlist.txt'

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
    return list(content_set)

# 处理去重内容，并与域名对比
def process_and_filter_content(content_list, domain_list):
    new_list = []
    for content in content_list:
        if not any(content.startswith(domain) for domain in domain_list):
            new_list.append(content)
    return new_list

# 分类汇总
def classify_content(new_list):
    DOMAIN = []
    DOMAIN_SUFFIX = []
    for item in new_list:
        if item.startswith('.'):
            DOMAIN_SUFFIX.append(item)
        else:
            DOMAIN.append(item)
    return DOMAIN, DOMAIN_SUFFIX

# JSON 输出
def save_to_json(DOMAIN, DOMAIN_SUFFIX, url):
    result = {
        "version": 1,
        "rules": [
            {
                "DOMAIN": DOMAIN,
                "DOMAIN_SUFFIX": DOMAIN_SUFFIX
            }
        ]
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
        print(f"Successfully converted JSON to {srs_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting JSON to SRS: {e}")


# 主函数
def main():
    os.mkdir(output_dir)

    # 读取域名列表
    with open(domain_file, 'r') as file:
        domain_list = file.read().splitlines()

    # 读取 URL 链接
    urls = read_urls_from_file(b_file)

    # 获取内容并去重
    deduplicated_content = fetch_and_deduplicate_content(urls)

    # 处理内容并过滤
    new_list = process_and_filter_content(deduplicated_content, domain_list)

    # 分类汇总
    DOMAIN, DOMAIN_SUFFIX = classify_content(new_list)

    # 输出到 JSON 文件
    filepath = save_to_json(DOMAIN, DOMAIN_SUFFIX, b_file)
    files.append(filepath)
    
    # 转换 JSON 为 SRS 文件
    convert_json_to_srs(filepath)

if __name__ == "__main__":
    main()
