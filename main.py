# -*- coding: utf-8 -*-
"""
百度AI图像识别小项目 - 智能图片内容识别器
使用百度通用物体和场景识别 API
API Key 通过环境变量读取，不硬编码在代码中
"""

import os
import base64
import requests
from pathlib import Path


def get_access_token():
    """
    通过 API Key 和 Secret Key 获取百度 access_token
    从环境变量读取，避免密钥泄露
    """
    # api_key = os.environ.get("BAIDU_API_XG9Va6EexJ7uAGzysnPJo8hbKEY")
    # secret_key = os.environ.get("BAIDU_SECRET_KEY")
    api_key = "XG9Va6EexJ7uAGzysnPJo8hb"
    secret_key = "JG5ygCODlNaKAaMkyCPPXQm0rHQTbYdf"
    
    

    if not api_key or not secret_key:
        raise EnvironmentError(
            "未找到环境变量 BAIDU_API_KEY 或 BAIDU_SECRET_KEY\n"
            "请先设置环境变量：\n"
            "  Windows CMD:  set BAIDU_API_KEY=你的APIKey\n"
            "                set BAIDU_SECRET_KEY=你的SecretKey\n"
            "  PowerShell:   $env:BAIDU_API_KEY='你的APIKey'\n"
            "                $env:BAIDU_SECRET_KEY='你的SecretKey'"
        )

    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    result = response.json()

    if "access_token" not in result:
        raise RuntimeError(f"获取 access_token 失败：{result}")

    return result["access_token"]


def image_to_base64(image_path: str) -> str:
    """将本地图片文件转为 base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def recognize_image(image_path: str, access_token: str) -> dict:
    """
    调用百度通用物体和场景识别 API
    :param image_path: 本地图片路径
    :param access_token: 百度 access_token
    :return: 识别结果字典
    """
    url = (
        "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
        f"?access_token={access_token}"
    )

    img_base64 = image_to_base64(image_path)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"image": img_base64}

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()


def print_results(result: dict, image_path: str):
    """格式化打印识别结果"""
    print("\n" + "=" * 55)
    print(f"  图片路径：{image_path}")
    print("=" * 55)

    if "error_code" in result:
        print(f"  识别失败：{result.get('error_msg', '未知错误')}")
        return

    items = result.get("result", [])
    if not items:
        print("  未识别到任何内容")
        return

    print(f"  共识别到 {len(items)} 个标签：\n")
    for i, item in enumerate(items, 1):
        keyword = item.get("keyword", "未知")
        score = item.get("score", 0)
        filled = int(score * 20)
        bar = "#" * filled + "-" * (20 - filled)
        print(f"  {i:2d}. {keyword:<18} {score:.4f}  [{bar}]")

    print("=" * 55)


def main():
    print("=" * 55)
    print("       百度AI 通用图像识别器")
    print("=" * 55)

    # 获取图片路径
    image_path = input("\n请输入图片路径（支持 jpg/png/bmp）：").strip().strip('"')

    if not Path(image_path).exists():
        print(f"\n文件不存在：{image_path}")
        return

    print("\n正在获取 access_token ...")
    try:
        token = get_access_token()
        print("access_token 获取成功！")
    except EnvironmentError as e:
        print(f"\n[错误] 环境变量未设置：\n{e}")
        return
    except Exception as e:
        print(f"\n[错误] 获取 token 失败：{e}")
        return

    print("正在识别图片，请稍候 ...")
    try:
        result = recognize_image(image_path, token)
        print_results(result, image_path)
    except Exception as e:
        print(f"\n[错误] 识别失败：{e}")
        return

    input("\n按 Enter 键退出 ...")


if __name__ == "__main__":
    main()
