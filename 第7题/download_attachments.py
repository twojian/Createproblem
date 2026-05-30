import os
import requests
import time

SAVE_DIR = r"d:\Projects\构建难题\第7题\附件下载"
os.makedirs(SAVE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

FILES = [
    {
        "url": "https://www.caict.ac.cn/kxyj/qwfb/bps/202602/P020260202487301304903.pdf",
        "filename": "附件1-人工智能产业发展研究报告（2025年）.pdf",
    },
    {
        "url": "https://hulianhutongshequ.cn/upload/tank/report/2025/202503/3/5fe899d5e59841d8aae129e9ff0d593d.pdf",
        "filename": "附件2-2025年AI技术人才供需洞察报告（猎聘大数据）.pdf",
    },
    {
        "url": "https://hulianhutongshequ.cn/upload/tank/report/2025/202506/3/6f2bcefc74f64537acd1474a0533ef2c.pdf",
        "filename": "附件3-2025年中国人工智能产业人才报告（智联猎头）.pdf",
    },
    {
        "url": "https://www.etc.org.cn/UserFiles/Article/findings/e8a71813-0fba-4bf1-aad8-9de5666f3b49.pdf",
        "filename": "附件4-2024年度AI人才供需与培养研究报告.pdf",
    },
    {
        "url": "https://hrss.gd.gov.cn/attachment/0/565/565456/4522123.pdf",
        "filename": "附件5-广东省人力资源市场工资价位及行业人工成本信息（2024年）.pdf",
    },
    {
        "url": "https://www.mohrss.gov.cn/SYrlzyhshbzb/zwgk/szrs/tjgb/202506/W020250616518526345602.pdf",
        "filename": "附件6-2024年度人力资源和社会保障事业发展统计公报.pdf",
    },
]

def download_file(url, filepath, timeout=120):
    print(f"正在下载: {os.path.basename(filepath)}")
    print(f"  URL: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = downloaded * 100 // total
                    print(f"\r  进度: {pct}% ({downloaded}/{total} bytes)", end="")
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"\n  完成: {size_mb:.2f} MB")
        return True
    except Exception as e:
        print(f"\n  失败: {e}")
        return False

def main():
    success = 0
    fail = 0

    for item in FILES:
        filepath = os.path.join(SAVE_DIR, item["filename"])
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"已存在 ({size_mb:.2f} MB): {item['filename']}")
            success += 1
            continue
        if download_file(item["url"], filepath):
            success += 1
        else:
            fail += 1
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"PDF下载完成: 成功 {success}, 失败 {fail}")

if __name__ == "__main__":
    main()