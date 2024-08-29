import subprocess

def get_hidden_branch_file_path():
    # 切换到 hidden 分支
    subprocess.run(['git', 'checkout', 'hidden'], check=True)
    
    # 获取 list.txt 文件的路径
    file_path = 'blacklist.txt'
    
    return file_path

path = get_hidden_branch_file_path()
print(path)
