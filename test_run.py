# -*- coding: utf-8 -*-
import os, base64, requests

api_key = os.environ.get("BAIDU_API_KEY")
secret_key = os.environ.get("BAIDU_SECRET_KEY")

# 获取 token
resp = requests.post("https://aip.baidubce.com/oauth/2.0/token", params={
    "grant_type": "client_credentials",
    "client_id": api_key,
    "client_secret": secret_key,
})
token = resp.json()["access_token"]
print("access_token 获取成功")

# 读取图片
img_path = r"C:\Users\Yang17818\Pictures\icon\01.png"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

# 调用识别 API
url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token=" + token
result = requests.post(
    url,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={"image": img_b64}
).json()

print()
print("=" * 55)
print("  图片：C:\\Users\\Yang17818\\Pictures\\icon\\01.png")
print("=" * 55)

if "error_code" in result:
    msg = result.get("error_msg", "未知错误")
    print("  识别失败：" + msg)
else:
    items = result.get("result", [])
    print("  共识别到 " + str(len(items)) + " 个标签：")
    print()
    for i, item in enumerate(items, 1):
        kw = item.get("keyword", "未知")
        sc = item.get("score", 0)
        filled = int(sc * 20)
        bar = "#" * filled + "-" * (20 - filled)
        print("  {:2d}. {:<18} {:.4f}  [{}]".format(i, kw, sc, bar))

print("=" * 55)
