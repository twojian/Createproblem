import os
import re
import sys
import shutil
import subprocess
import requests
import urllib3
import pandas as pd

# ================= 配置区域 =================
INPUT_FILE = "tasks.txt"
BASE_DIR = r"D:\Projects\构建难题"
SIZE_VALIDATE_THRESHOLD = 512 * 1024
# ===========================================

def parse_tasks(file_path):
    """
    改进的接口函数：使用更宽松的正则匹配长标题和带空格的标题
    """
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 改进的正则表达式：
    # 1. (附件\d+-.+?\.(?:pdf|csv|xlsx|xls|docx|doc|txt|html)) -> 匹配多种文件格式
    # 2. \s+ -> 匹配中间的换行或空格
    # 3. (https?://[^\s]+) -> 匹配紧随其后的网址
    pattern = r"(附件\d+-.+?\.(?:pdf|csv|xlsx|xls|docx|doc|txt|html))\s+(https?://[^\s]+)"
    
    # 使用 re.DOTALL 确保匹配不受换行干扰，但这里我们更倾向于逐个提取
    matches = re.findall(pattern, content)
    
    # 清洗掉标题末尾可能的冗余空格
    return {name.strip(): url.strip() for name, url in matches}

def save_links_to_file(tasks, folder):
    """将附件链接保存到题目文件夹中的txt文件"""
    links_file = os.path.join(folder, "附件链接.txt")
    
    with open(links_file, "w", encoding="utf-8") as f:
        for name, url in tasks.items():
            f.write(f"{name}\n")
            f.write(f"{url}\n")
            f.write("\n")
    
    print(f"\n✅ 附件链接已保存到: {links_file}")


def validate_download(file_path, expected_size):
    if expected_size is None:
        return True, os.path.getsize(file_path), "无Content-Length头，跳过校验"

    actual_size = os.path.getsize(file_path)
    if actual_size == expected_size:
        return True, actual_size, f"校验通过 ({actual_size:,} bytes)"
    else:
        diff = expected_size - actual_size
        return False, actual_size, f"校验失败！期望 {expected_size:,} bytes，实际 {actual_size:,} bytes，缺少 {diff:,} bytes"


def _try_download_with_requests(url, file_path, timeout, use_verify, headers_override=None):
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/pdf,text/html,*/*"
    }
    headers = headers_override if headers_override else default_headers

    resp = requests.get(url, headers=headers, timeout=timeout, stream=True, verify=use_verify)
    resp.raise_for_status()
    expected_size = resp.headers.get('Content-Length')
    if expected_size:
        expected_size = int(expected_size)

    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    return True, expected_size


def _try_download_with_curl(url, file_path, timeout):
    curl_path = shutil.which("curl")
    if curl_path is None:
        raise RuntimeError("系统中未找到curl命令")

    result = subprocess.run(
        [curl_path, "-L", "-o", file_path, "--connect-timeout", str(timeout),
         "--max-time", str(timeout * 2), "-k", "-s", "-S", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl退出码 {result.returncode}: {result.stderr.strip()}")

    expected_size = None
    head_result = subprocess.run(
        [curl_path, "-sI", "-L", "-k", url],
        capture_output=True, text=True
    )
    cl_match = re.search(r'content-length:\s*(\d+)', head_result.stdout, re.IGNORECASE)
    if cl_match:
        expected_size = int(cl_match.group(1))

    return True, expected_size


def download_with_fallback(url, file_path, timeout=120):
    backup_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    ]

    strategies = [
        ("默认策略(verify=False)", lambda: _try_download_with_requests(url, file_path, timeout, use_verify=False)),
        ("TLS严格验证", lambda: _try_download_with_requests(url, file_path, timeout, use_verify=True)),
        ("备用UA-Firefox", lambda: _try_download_with_requests(
            url, file_path, timeout, use_verify=False,
            headers_override={"User-Agent": backup_user_agents[0], "Accept": "application/pdf,text/html,*/*"}
        )),
        ("备用UA-Safari", lambda: _try_download_with_requests(
            url, file_path, timeout, use_verify=False,
            headers_override={"User-Agent": backup_user_agents[1], "Accept": "application/pdf,text/html,*/*"}
        )),
        ("备用UA-Linux", lambda: _try_download_with_requests(
            url, file_path, timeout, use_verify=False,
            headers_override={"User-Agent": backup_user_agents[2], "Accept": "application/pdf,text/html,*/*"}
        )),
        ("curl回退", lambda: _try_download_with_curl(url, file_path, timeout)),
    ]

    last_error = None
    for strategy_name, strategy_fn in strategies:
        try:
            print(f"    尝试策略: {strategy_name}")
            success, expected_size = strategy_fn()
            if success:
                return True, f"{strategy_name} 成功", expected_size
        except Exception as e:
            last_error = str(e)
            print(f"    {strategy_name} 失败: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            continue

    return False, f"所有策略均失败，最后错误: {last_error}", None


def download_engine(tasks, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    save_links_to_file(tasks, folder)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print(f"已识别到 {len(tasks)} 个下载任务...")

    for name, url in tasks.items():
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", name)
        file_path = os.path.join(folder, safe_name)

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"[-] 跳过已存在: {safe_name} ({file_size:,} bytes)")
            continue

        target_is_xlsx = name.lower().endswith('.xlsx') and 'csv' in url.lower()
        download_path = file_path
        if target_is_xlsx:
            download_path = os.path.join(folder, safe_name.replace('.xlsx', '.csv'))

        print(f"[+] 正在下载: {safe_name}")
        success, message, expected_size = download_with_fallback(url, download_path)

        if not success:
            print(f"    最终失败 ❌: {message}")
            continue

        validated = True
        validate_msg = ""
        if expected_size is not None or os.path.getsize(download_path) >= SIZE_VALIDATE_THRESHOLD:
            validated, actual_size, validate_msg = validate_download(download_path, expected_size)
            if not validated:
                print(f"    ⚠️ 大小校验不通过: {validate_msg}")
                print(f"    保留已下载文件，请手动检查")
            else:
                print(f"    📏 {validate_msg}")

        if target_is_xlsx:
            print(f"    转换 CSV -> XLSX...")
            try:
                df = pd.read_csv(download_path)
                df.to_excel(file_path, index=False, engine='openpyxl')
                os.remove(download_path)
                print(f"    转换成功 ✅")
            except Exception as e:
                print(f"    转换失败 ❌: {e}")
        else:
            status = "✅" if validated else "⚠️ (大小异常但已保留)"
            print(f"    {message} {status}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python download.py <题号>")
        print("示例: python download.py 4")
        sys.exit(1)

    question_num = sys.argv[1]
    SAVE_DIR = os.path.join(BASE_DIR, f"第{question_num}题")

    task_map = parse_tasks(INPUT_FILE)

    if task_map:
        download_engine(task_map, SAVE_DIR)
    else:
        print("未识别到任务，请确保 tasks.txt 内容包含 '附件X-...pdf' 格式及其下方的链接。")

    print("\n任务结束。")