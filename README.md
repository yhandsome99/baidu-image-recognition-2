# 百度AI 通用图像识别器 -423830113-付标

基于百度AI开放平台的图像识别小项目，使用 PyCharm 开发。

## 项目简介

输入一张本地图片，程序自动调用百度通用物体和场景识别 API，识别图片中的物体/场景，并以置信度排序展示结果。

**创新点：**
- API Key 通过环境变量读取，不硬编码在代码中，安全可靠
- 识别结果带可视化进度条，直观展示置信度
- 代码结构清晰，函数职责单一，易于扩展

## 项目结构

```
baidu_image_recognition/
├── main.py           # 主程序
├── requirements.txt  # 依赖列表
├── env_example.txt   # 环境变量配置示例
├── .gitignore        # 忽略 .env 文件，防止密钥泄露
└── README.md         # 项目说明
```

## 环境准备

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量（重要！不要把 Key 写进代码）

**Windows CMD：**
```cmd
set BAIDU_API_KEY=你的APIKey
set BAIDU_SECRET_KEY=你的SecretKey
```

**Windows PowerShell：**
```powershell
$env:BAIDU_API_KEY = "你的APIKey"
$env:BAIDU_SECRET_KEY = "你的SecretKey"
```

> 也可以在 PyCharm 的运行配置（Run/Debug Configurations）→ Environment variables 中填写，这样每次运行自动生效。

### 3. 运行程序

```bash
python main.py
```

## 使用示例

```
=======================================================
       百度AI 通用图像识别器
=======================================================

请输入图片路径（支持 jpg/png/bmp）：C:\Users\test\cat.jpg

正在获取 access_token ...
access_token 获取成功！
正在识别图片，请稍候 ...

=======================================================
  图片路径：C:\Users\test\cat.jpg
=======================================================
  共识别到 5 个标签：

   1. 猫                 0.9823  [###################-]
   2. 宠物               0.9541  [##################--]
   3. 动物               0.8876  [#################---]
   4. 橘猫               0.7234  [##############------]
   5. 室内               0.5012  [##########----------]
=======================================================
```

## API 说明

使用百度AI开放平台「通用物体和场景识别」接口：
- 接口文档：https://ai.baidu.com/ai-doc/IMAGERECOGNITION/Xk3bcxe21
- 支持识别超过10万种物体和场景
- 返回结果包含标签名称和置信度分数

## 注意事项

- `.env` 文件和 API Key 不要上传到代码仓库（已在 `.gitignore` 中配置）
- 图片大小建议不超过 4MB
- 支持 jpg、png、bmp 格式
