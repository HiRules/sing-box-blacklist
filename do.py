import os
import requests
import json
import subprocess

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
            content_set.add(response.text.strip())
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
def save_to_json(DOMAIN, DOMAIN_SUFFIX, output_filepath):
    result = {
        "DOMAIN": DOMAIN,
        "DOMAIN_SUFFIX": DOMAIN_SUFFIX
    }
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)  # 创建目录
    with open(output_filepath, 'w') as json_file:
        json.dump(result, json_file, indent=4)

# 使用sing-box将JSON转换为.srs格式
def convert_json_to_srs(srs_file, json_file):
    # sing-box的命令需要根据您的使用情况来调整
    try:
        subprocess.run(['sing-box rule-set compile --output ', srs_file, ' ', json_file], check=True)
        print(f"Successfully converted JSON to {srs_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Error converting JSON to SRS: {e}")


# 主函数
def main():
    files = []
    url_file = 'blacklist.txt'  # 输入的 URL 文件
    domain_file = 'excludecustomlist.txt'  # 存放需比较的域名列表文件
    output_directory = './release'  # 输出目录
    output_file_JSON = os.path.join(output_directory, 'blacklist.json')  # 输出的 JSON 文件
    output_file_SRS = os.path.join(output_directory, 'blacklist.srs')  # 输出的 SRS 文件
    
    # 检查输入文件是否存在
    if not os.path.exists(url_file):
        print(f"Error: The file '{url_file}' does not exist.")
        return
    if not os.path.exists(domain_file):
        print(f"Error: The file '{domain_file}' does not exist.")
        return

    # 读取域名列表
    with open(domain_file, 'r') as file:
        domain_list = file.read().splitlines()

    # 读取 URL 链接
    urls = read_urls_from_file(url_file)

    # 获取内容并去重
    deduplicated_content = fetch_and_deduplicate_content(urls)

    # 处理内容并过滤
    new_list = process_and_filter_content(deduplicated_content, domain_list)

    # 分类汇总
    DOMAIN, DOMAIN_SUFFIX = classify_content(new_list)

    # 输出到 JSON 文件
    save_to_json(DOMAIN, DOMAIN_SUFFIX, output_file_JSON)
    print(f"Output successfully saved to '{output_file_JSON}'.")
    
    # 转换 JSON 到 SRS 文件
    output_file_SRS = output_file_JSON.replace(".json", ".srs")
    os.system("sing-box rule-set compile --output " + output_file_SRS + " " + output_file_JSON)
    print(f"Output successfully saved to '{output_file_SRS}'.")

if __name__ == "__main__":
    main()
