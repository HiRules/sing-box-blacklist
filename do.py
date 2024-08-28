import requests
import os

proxylist = [
    "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/proxy.txt",
    "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/gfw.txt"
]

excludelist = [
    "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/apple.txt",
    "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/icloud.txt",
    "https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/google.txt"
]

output_dir = "./release"
files = []


def convert_proxylist(url: str) -> str:
    r = requests.get(url)
    domain_list = domain_suffix_list = []
    if r.status_code == 200:
        lines = r.text.splitlines()
        for line in lines:
            if not line.startswith("."):
                domain_list.append(line.group(1))
            else:
                domain_suffix_list.append(line.group(1))
                    
    result = domain_suffix_list
    filename = url.split("/")[-1]
    if "-" in filename:
        prefix = filename.split("-")[0]
    else:
        prefix = filename.split(".")[0]
    filepath = os.path.join(output_dir, "cn_" + prefix + ".txt")
    with open(filepath, "w") as f:
        f.write("\n".join(result))
    return filepath


def merge_domains(filename, *lists):
    result = set()
    for i in range(len(lists)):
        with open(lists[i],"r",encoding="utf-8") as R:
            for line in R:
                e = line.strip()
                if e:
                    result.add(e)
    result = sorted(result)
    filepath = os.path.join(output_dir, filename + ".txt")
    with open(filepath,"w",encoding="utf-8") as W:
        for line in result:
            W.write(line + "\n")
    return filepath
    

def convert_site(tmp: str) -> str:
    domain_suffix_list = []
    with open(tmp,"r",encoding="utf-8") as lines:
        for line in lines:
            domain_suffix_list.append(line.strip())
    result = {
        "version": 1,
        "rules": [
            {
                "domain_suffix": []
            }
        ]
    }
    result["rules"][0]["domain_suffix"] = domain_suffix_list
    filename = tmp.split("/")[-1]
    filepath = os.path.join(output_dir, filename.rsplit(".",1)[0] + ".json")
    with open(filepath, "w") as f:
        f.write(json.dumps(result, indent=4))
    return filepath


CNSITE_ALL = merge_domains("CNSITE_ALL", *[files[0], files[1], files[2]])
files.append(CNSITE_ALL)

os.mkdir(output_dir)
for url in proxylist:
    filepath = convert_dnsmasq(url)
    files.append(filepath)


def convert_gfwlist(url: str) -> str:
    r = requests.get(url)
    domain_suffix_list = []
    prefix = str()
    if r.status_code == 200:
        lines = r.text.splitlines()
        for line in lines:
            if not line.startswith("#"):
                domain = re.match(r"server=\/(.*)\/(.*)", line)
                if domain:
                    domain_suffix_list.append(domain.group(1))
    result = domain_suffix_list
    filename = url.split("/")[-1]
    if "-" in filename:
        prefix = filename.split("-")[0]
    else:
        prefix = filename.split(".")[0]
    filepath = os.path.join(output_dir, "cn_" + prefix + ".txt")
    with open(filepath, "w") as f:
        f.write("\n".join(result))
    return filepath


def convert_chnroutes2(url: str) -> str:
    r = requests.get(url)
    ip_cidr_list = []
    prefix = str()
    if r.status_code == 200:
        lines = r.text.splitlines()
        for line in lines:
            if not line.startswith("#"):
                ip_cidr_list.append(line)
    result = ip_cidr_list
    filename = url.split("/")[-1]
    if "-" in filename:
        prefix = "GeoIP2CN"
    else:
        prefix = filename.split(".")[-2]
    filepath = os.path.join(output_dir, prefix + ".txt")
    with open(filepath, "w") as f:
        f.write("\n".join(result))
    return filepath


def main():
    os.mkdir(output_dir)
    global files
    for url in dnsmasq_china_list:
        filepath = convert_dnsmasq(url)
        files.append(filepath)
    for url in chnroutes2:
        filepath = convert_chnroutes2(url)
        files.append(filepath)
    for url in iwik:
        filepath = convert_iwik(url)
        files.append(filepath)
    for url in apnic:
        filepath = convert_apnic(url, "CN", "ipv4")
        files.append(filepath)
        filepath = convert_apnic(url, "CN", "ipv6")
        files.append(filepath)
    for url in maxmind:
        filepath = convert_maxmind(url, "CN", "ipv4")
        files.append(filepath)
        filepath = convert_maxmind(url, "CN", "ipv6")
        files.append(filepath)
    
    # files[0] = os.path.join(output_dir, accelerated-domains.china.txt)
    # files[1] = os.path.join(output_dir, apple.china.txt)
    # files[2] = os.path.join(output_dir, google.china.txt)
    # files[3] = os.path.join(output_dir, chnroutes.txt)
    # files[4] = os.path.join(output_dir, GeoIP2CN.txt)
    # files[5] = os.path.join(output_dir, iwik_ipv4.txt)
    # files[6] = os.path.join(output_dir, iwik_ipv6.txt)
    # files[7] = os.path.join(output_dir, apnic_ipv4.txt)
    # files[8] = os.path.join(output_dir, apnic_ipv6.txt)
    # files[9] = os.path.join(output_dir, maxmind_ipv4.txt)
    # files[10] = os.path.join(output_dir, maxmind_ipv6.txt)
    
    CNSITE_ALL = merge_domains("CNSITE_ALL", *[files[0], files[1], files[2]])
    files.append(CNSITE_ALL)
     
    #CNIPV4_ALL = merge_cidr("CNIPV4_ALL", *[files[3], files[4], files[5], files[7], files[9]])
    #files.append(CNIPV4_ALL)
    
    #CNIPV6_ALL = merge_cidr("CNIPV6_ALL", *[files[6], files[8], files[10]])
    #files.append(CNIPV6_ALL)
    
    # files[11] = os.path.join(output_dir, CNSITE_ALL.txt)
    # files[12] = os.path.join(output_dir, CNIPV4_ALL.txt)
    # files[13] = os.path.join(output_dir, CNIPV6_ALL.txt)
    
    return files


if __name__ == "__main__":
    files = main()
