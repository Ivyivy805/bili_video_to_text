# 快速开始指南

## 🚀 10秒上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 提取字幕

```bash
# 方法1: 使用BV号
python main.py --bvid BV1xx411c7mD

# 方法2: 使用URL
python main.py --url "https://www.bilibili.com/video/BV1xx411c7mD"
```

## 📝 获取BV号的方法

1. 打开任意B站视频
2. 看地址栏: `https://www.bilibili.com/video/BV1xx411c7mD`
3. `BV1xx411c7mD` 就是BV号

## ✨ 核心功能

### ✅ 已实现

- ✅ 通过BV号获取视频信息
- ✅ 通过URL获取视频信息
- ✅ 自动提取字幕（支持多语言）
- ✅ 导出JSON格式（含时间轴）
- ✅ 导出SRT格式（标准字幕格式）
- ✅ 导出TXT格式（纯文本）
- ✅ 支持Cookie登录（访问需要登录的视频）

### ⚠️ 限制

- ⚠️ 只能提取UP主上传的字幕
- ⚠️ 不支持AI自动生成字幕
- ⚠️ 搜索功能可能需要登录凭证

## 📦 输出文件

运行后会在当前目录（或指定目录）生成：

```
BV1xx411c7mD_中文（中国）.json  # JSON格式，包含时间轴
BV1xx411c7mD_中文（中国）.srt   # SRT字幕格式
BV1xx411c7mD_中文（中国）.txt   # 纯文本格式
```

## 🔧 高级用法

### 指定输出目录

```bash
python main.py --bvid BV1xx411c7mD --output ./subtitles
```

### 使用Cookie登录

```bash
# 方法1: 命令行参数
python main.py --bvid BV1xx411c7mD \
  --sessdata "your_sessdata" \
  --bili-jct "your_bili_jct" \
  --buvid3 "your_buvid3"

# 方法2: 环境变量
export BILI_SESSDATA="your_sessdata"
export BILI_JCT="your_bili_jct"
export BILI_BUVID3="your_buvid3"
python main.py --bvid BV1xx411c7mD
```

### 交互模式

```bash
python main.py
```

然后按提示操作即可。

## 🛠️ 故障排除

### 问题：找不到字幕

**可能原因：**
- 该视频没有UP主上传的字幕
- 该视频只有AI自动生成的字幕（暂不支持）

**解决方法：**
- 尝试其他有字幕的视频
- 确认视频确实有字幕（在B站播放器设置中查看）

### 问题：搜索失败（403错误）

**可能原因：**
- B站搜索API需要验证

**解决方法：**
- 直接使用BV号或URL代替搜索
- 配置Cookie登录凭证

## 💡 小技巧

### 如何找到有字幕的视频？

1. 在B站搜索相关视频
2. 播放视频，点击播放器右下角的"CC"按钮
3. 如果能看到字幕选项，说明有字幕
4. 复制视频URL或BV号，使用本工具提取

### 推荐测试视频

可以使用以下类型的视频测试：
- TED演讲视频
- 教程视频
- 官方频道发布的视频
- 外语视频（通常有字幕）

## 📚 更多信息

- 详细文档: [README.md](README.md)
- 使用示例: [example_usage.md](example_usage.md)
- 问题反馈: GitHub Issues
