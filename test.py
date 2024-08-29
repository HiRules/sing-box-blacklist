
import subprocess

def get_hidden_branch_file_path():
    try:
        # 切换到 hidden 分支
        subprocess.run(['git', 'checkout', 'hidden'], check=True)
        
        # 获取 list.txt 文件的路径
        file_path = 'blacklist.txt'
        
        return file_path
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return None

path = get_hidden_branch_file_path()
if path:
    print(path)
else:
    print("Failed to switch to hidden branch.")
