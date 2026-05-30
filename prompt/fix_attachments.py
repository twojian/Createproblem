import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

save_dir = r"D:\Projects\构建难题\第3题"

# 附件6: eVTOL技术参数对比论文
print("[+] 下载附件6...")
try:
    url = "https://learning-gate.com/index.php/2576-8484/article/download/4156/1618/5973"
    r = requests.get(url, headers=headers, timeout=120, verify=False, stream=True)
    ct = r.headers.get("content-type", "unknown")
    print(f"    状态码: {r.status_code}, Content-Type: {ct}")
    if r.status_code == 200:
        path = os.path.join(save_dir, "附件6-全球主要eVTOL企业技术参数对比表.pdf")
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        size = os.path.getsize(path)
        print(f"    成功, 大小: {size} bytes")
except Exception as e:
    print(f"    失败: {e}")

# 附件7: 新华网低空经济研究报告
print("[+] 下载附件7...")
try:
    url = "https://imgs.xinhuanet.com/info/20250813/01e3f71d8b884bb5aa6bfaa4a3f840ee/20250813e642284144084df4bc1c50db199b3bb3_275281ee6199b0442ea760200c0cea32cc.pdf"
    r = requests.get(url, headers=headers, timeout=120, verify=False, stream=True)
    ct = r.headers.get("content-type", "unknown")
    print(f"    状态码: {r.status_code}, Content-Type: {ct}")
    if r.status_code == 200:
        path = os.path.join(save_dir, "附件7-中国各省市低空经济试点政策汇总.pdf")
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        size = os.path.getsize(path)
        print(f"    成功, 大小: {size} bytes")
except Exception as e:
    print(f"    失败: {e}")

# 附件8: 36kr低空物流成本文章
print("[+] 下载附件8...")
try:
    url = "https://36kr.com/p/3730636477461000"
    r = requests.get(url, headers=headers, timeout=120, verify=False, stream=True)
    ct = r.headers.get("content-type", "unknown")
    print(f"    状态码: {r.status_code}, Content-Type: {ct}")
    if r.status_code == 200:
        path = os.path.join(save_dir, "附件8-典型应用场景成本模型测算底表.html")
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        size = os.path.getsize(path)
        print(f"    成功, 大小: {size} bytes")
except Exception as e:
    print(f"    失败: {e}")

print("\n下载完成")
