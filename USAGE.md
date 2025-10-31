# 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 Cookies

首次使用需要配置B站的cookies：

```bash
python main.py config
```

按照提示输入从浏览器中获取的cookie值。

#### 如何获取 Cookies

1. 用浏览器访问 https://www.bilibili.com 并登录
2. 按 **F12** 打开开发者工具
3. 切换到 **Application** (Chrome/Edge) 或 **存储** (Firefox) 标签
4. 在左侧找到 **Cookies** -> **https://www.bilibili.com**
5. 复制以下三个cookie的值：
   - `SESSDATA`
   - `bili_jct`
   - `buvid3`

![获取Cookies示例](https://i.imgur.com/example.png)

### 3. 搜索视频

```bash
# 搜索关键词
python main.py search "Python教程"

# 限制结果数量
python main.py search "Python教程" --limit 5
```

输出示例：
```
搜索: Python教程

找到 10 个结果:

1. Python零基础入门教程
   作者: 某UP主
   时长: 01:30:45
   播放: 1234567
   BV号: BV1xx411c7mD
   URL: https://www.bilibili.com/video/BV1xx411c7mD

...
```

### 4. 查看视频信息

在提取字幕前，可以先查看视频是否有字幕：

```bash
python main.py info BV1xx411c7mD
```

或者使用完整URL：

```bash
python main.py info https://www.bilibili.com/video/BV1xx411c7mD
```

输出示例：
```
=== 视频信息 ===
标题: Python零基础入门教程
作者: 某UP主
时长: 5445秒
播放: 1234567
点赞: 12345

简介:
这是一个Python入门教程...

=== 字幕信息 ===
该视频有 2 个字幕:
  - 中文（中国） (zh-CN)
    贡献者: 字幕君
  - English (en-US)
```

### 5. 提取字幕

#### 基本用法

```bash
# 使用BV号
python main.py extract BV1xx411c7mD

# 使用完整URL
python main.py extract https://www.bilibili.com/video/BV1xx411c7mD
```

#### 高级选项

```bash
# 指定输出格式 (srt, txt, json)
python main.py extract BV1xx411c7mD --format srt

# 指定输出目录
python main.py extract BV1xx411c7mD --output ./my_subtitles

# 只下载特定语言的字幕
python main.py extract BV1xx411c7mD --language zh-CN

# 组合使用
python main.py extract BV1xx411c7mD \
  --format txt \
  --language en-US \
  --output ./english_subs
```

#### 输出格式说明

- **SRT** - 标准字幕格式，包含时间轴，适合视频播放器
- **TXT** - 纯文本格式，只包含字幕文本
- **JSON** - 原始JSON格式，包含完整的时间和文本信息

### 6. 批量提取

可以创建一个简单的脚本批量提取：

```bash
#!/bin/bash
# batch_extract.sh

videos=(
  "BV1xx411c7mD"
  "BV1yy411c8mE"
  "BV1zz411c9mF"
)

for bvid in "${videos[@]}"; do
  echo "提取 $bvid..."
  python main.py extract "$bvid"
done
```

## 常见问题

### Q: 提示"该视频没有字幕"怎么办？

A: 这说明该视频确实没有UP主或官方提供的CC字幕。本工具只能提取CC字幕（软字幕），不能提取嵌入视频画面中的硬字幕。

如果需要提取硬字幕，可以考虑使用OCR工具。

### Q: 提示API错误或cookies失效？

A: Cookies有效期约为1个月，过期后需要重新配置：

```bash
python main.py config
```

### Q: 如何清除配置？

```bash
python main.py config --clear
```

### Q: 字幕文件保存在哪里？

A: 默认保存在 `subtitles/` 目录下，文件名格式为：
```
{视频标题}_{BV号}_{语言代码}.{格式}
```

例如：
```
Python零基础入门教程_BV1xx411c7mD_zh-CN.srt
```

### Q: 能不能不配置cookies？

A: 不配置cookies可以使用搜索功能，但无法提取字幕。B站的字幕API需要登录态才能访问。

## 进阶用法

### 作为Python模块使用

```python
from bilibili_api import BilibiliAPI
from subtitle_handler import SubtitleExtractor
from config_manager import ConfigManager

# 加载配置
config = ConfigManager()
cookies = config.get_cookies()

# 初始化API
api = BilibiliAPI(cookies)

# 搜索视频
results = api.search_videos("Python教程")
for video in results:
    print(video['title'], video['bvid'])

# 提取字幕
extractor = SubtitleExtractor(api)
saved_files = extractor.extract_and_save(
    bvid="BV1xx411c7mD",
    output_dir="subtitles",
    format="srt"
)
```

### 直接调用API

```python
from bilibili_api import BilibiliAPI

api = BilibiliAPI(cookies)

# 获取视频信息
info = api.get_video_info("BV1xx411c7mD")
print(info['title'])

# 获取字幕列表
subtitle_list = api.get_subtitle_list("BV1xx411c7mD")
for sub in subtitle_list:
    print(sub['language'], sub['subtitle_url'])

# 下载字幕内容
subtitle_data = api.download_subtitle(subtitle_url)
```

## 技术细节

### API端点

本工具使用以下B站API：

- 搜索: `https://api.bilibili.com/x/web-interface/search/type`
- 视频信息: `https://api.bilibili.com/x/web-interface/view`
- 字幕: `https://api.bilibili.com/x/player/wbi/v2`

### 字幕数据格式

B站返回的字幕数据格式为JSON：

```json
[
  {
    "from": 0.0,
    "to": 2.5,
    "content": "这是第一句字幕"
  },
  {
    "from": 2.5,
    "to": 5.0,
    "content": "这是第二句字幕"
  }
]
```

### SRT格式转换

工具会自动将JSON格式转换为标准SRT格式：

```srt
1
00:00:00,000 --> 00:00:02,500
这是第一句字幕

2
00:00:02,500 --> 00:00:05,000
这是第二句字幕
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
