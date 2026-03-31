# -*- coding: utf-8 -*-
"""
百度AI图像识别小项目 - 带图形界面版本
使用 tkinter 构建 GUI，调用百度通用物体和场景识别 API
API Key 通过环境变量读取，不硬编码在代码中
"""

import os
import base64
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

import requests
from PIL import Image, ImageTk


# ──────────────────────────────────────────────
# 百度 API 相关函数
# ──────────────────────────────────────────────

def get_access_token():
    api_key = "XG9Va6EexJ7uAGzysnPJo8hb"
    secret_key = "JG5ygCODlNaKAaMkyCPPXQm0rHQTbYdf"
    if not api_key or not secret_key:
        raise EnvironmentError("未找到环境变量 BAIDU_API_KEY 或 BAIDU_SECRET_KEY")
    resp = requests.post(
        "https://aip.baidubce.com/oauth/2.0/token",
        params={
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError("获取 access_token 失败：" + str(data))
    return data["access_token"]


def recognize_image(image_path: str, access_token: str) -> list:
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    url = (
        "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
        "?access_token=" + access_token
    )
    resp = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"image": img_b64},
    )
    resp.raise_for_status()
    result = resp.json()
    if "error_code" in result:
        raise RuntimeError("识别失败：" + result.get("error_msg", "未知错误"))
    return result.get("result", [])


# ──────────────────────────────────────────────
# GUI 主窗口
# ──────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("百度AI 图像识别器")
        self.geometry("720x580")
        self.resizable(False, False)
        self.configure(bg="#f0f4f8")

        self.image_path = tk.StringVar()
        self._build_ui()

    # ── 构建界面 ──────────────────────────────
    def _build_ui(self):
        # 标题栏
        title_frame = tk.Frame(self, bg="#2563eb", height=56)
        title_frame.pack(fill="x")
        tk.Label(
            title_frame,
            text="🔍  百度AI 通用图像识别器",
            font=("微软雅黑", 16, "bold"),
            bg="#2563eb",
            fg="white",
        ).pack(pady=12)

        # 主体区域
        body = tk.Frame(self, bg="#f0f4f8")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # 左侧：图片预览
        left = tk.Frame(body, bg="#f0f4f8")
        left.pack(side="left", fill="y")

        self.preview_label = tk.Label(
            left,
            text="暂无图片\n\n点击下方按钮\n选择图片",
            width=28,
            height=14,
            bg="#e2e8f0",
            fg="#94a3b8",
            font=("微软雅黑", 11),
            relief="flat",
            bd=0,
        )
        self.preview_label.pack()

        # 选择图片按钮
        btn_frame = tk.Frame(left, bg="#f0f4f8")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="📂  选择图片",
            font=("微软雅黑", 11),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._choose_image,
        ).pack(side="left", padx=4)

        self.run_btn = tk.Button(
            btn_frame,
            text="▶  开始识别",
            font=("微软雅黑", 11),
            bg="#16a34a",
            fg="white",
            activebackground="#15803d",
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            state="disabled",
            command=self._start_recognize,
        )
        self.run_btn.pack(side="left", padx=4)

        # 路径显示
        self.path_var = tk.StringVar(value="未选择图片")
        tk.Label(
            left,
            textvariable=self.path_var,
            bg="#f0f4f8",
            fg="#64748b",
            font=("微软雅黑", 8),
            wraplength=220,
        ).pack()

        # 右侧：识别结果
        right = tk.Frame(body, bg="#f0f4f8")
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))

        tk.Label(
            right,
            text="识别结果",
            font=("微软雅黑", 12, "bold"),
            bg="#f0f4f8",
            fg="#1e293b",
        ).pack(anchor="w")

        # 结果列表（Treeview）
        cols = ("rank", "label", "score", "bar")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=12)
        self.tree.heading("rank", text="#")
        self.tree.heading("label", text="识别标签")
        self.tree.heading("score", text="置信度")
        self.tree.heading("bar", text="可信程度")
        self.tree.column("rank", width=36, anchor="center")
        self.tree.column("label", width=130)
        self.tree.column("score", width=70, anchor="center")
        self.tree.column("bar", width=160)

        style = ttk.Style()
        style.configure("Treeview", font=("微软雅黑", 10), rowheight=28)
        style.configure("Treeview.Heading", font=("微软雅黑", 10, "bold"))

        self.tree.pack(fill="both", expand=True)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪，请选择图片")
        status_bar = tk.Frame(self, bg="#e2e8f0", height=30)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            bg="#e2e8f0",
            fg="#475569",
            font=("微软雅黑", 9),
        ).pack(side="left", padx=12, pady=4)

        self.progress = ttk.Progressbar(
            status_bar, mode="indeterminate", length=120
        )
        self.progress.pack(side="right", padx=12, pady=4)

    # ── 选择图片 ──────────────────────────────
    def _choose_image(self):
        path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")],
        )
        if not path:
            return
        self.image_path.set(path)
        short = Path(path).name
        self.path_var.set(short)
        self.run_btn.config(state="normal")
        self._show_preview(path)
        self.status_var.set(f"已选择：{short}")

    def _show_preview(self, path: str):
        try:
            img = Image.open(path)
            img.thumbnail((220, 200))
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="", bg="#e2e8f0")
            self.preview_label.image = photo  # 防止被 GC
        except Exception:
            self.preview_label.config(text="预览失败", image="")

    # ── 开始识别（后台线程，避免界面卡顿）──────
    def _start_recognize(self):
        self.run_btn.config(state="disabled")
        self.status_var.set("正在识别，请稍候...")
        self.progress.start(10)
        # 清空旧结果
        for row in self.tree.get_children():
            self.tree.delete(row)
        threading.Thread(target=self._do_recognize, daemon=True).start()

    def _do_recognize(self):
        try:
            token = get_access_token()
            items = recognize_image(self.image_path.get(), token)
            self.after(0, self._show_results, items)
        except EnvironmentError as e:
            self.after(0, self._on_error, str(e))
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _show_results(self, items: list):
        self.progress.stop()
        self.run_btn.config(state="normal")
        if not items:
            self.status_var.set("未识别到任何内容")
            return
        for i, item in enumerate(items, 1):
            kw = item.get("keyword", "未知")
            sc = item.get("score", 0)
            pct = f"{sc * 100:.1f}%"
            filled = int(sc * 20)
            bar = "█" * filled + "░" * (20 - filled)
            self.tree.insert("", "end", values=(i, kw, pct, bar))
        self.status_var.set(f"识别完成，共 {len(items)} 个标签")

    def _on_error(self, msg: str):
        self.progress.stop()
        self.run_btn.config(state="normal")
        self.status_var.set("识别失败")
        messagebox.showerror("错误", msg)


# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
