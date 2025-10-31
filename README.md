# B站视频字幕提取工具

一个用于搜索B站视频并自动提取字幕的Python工具。

## 功能特性

- 🔍 **搜索B站视频** - 通过关键词搜索B站视频
- 📺 **获取视频信息** - 获取视频标题、作者、播放量等详细信息
- 📝 **提取字幕** - 自动提取视频字幕（支持多语言）
- 💾 **多种格式** - 支持导出JSON和SRT格式字幕
- 🚀 **简单易用** - 命令行界面，一键操作

## 安装

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd bili_video_to_text
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式一：通过BV号提取字幕

```bash
python main.py --bvid BV1xx411c7mD
```

### 方式二：搜索视频并提取

```bash
# 搜索视频
python main.py --search "Python教程"

# 从搜索结果选择视频并提取字幕
python main.py --bvid <选中的BV号>
```

### 方式三：直接使用URL

```bash
python main.py --url "https://www.bilibili.com/video/BV1xx411c7mD"
```

## 输出格式

字幕将保存为以下格式：
- `{视频标题}_subtitles.json` - JSON格式（包含时间轴）
- `{视频标题}_subtitles.srt` - SRT格式（通用字幕格式）

## 注意事项

- ⚠️ 仅支持提取UP主上传的字幕，不支持AI自动生成字幕
- ⚠️ 部分视频可能没有字幕
- ⚠️ 需要网络连接才能访问B站API

## 高级功能（可选）

如果需要访问需要登录才能看的视频，可以配置Cookie：

```bash
# 通过环境变量配置
export BILI_SESSDATA="your_sessdata"
export BILI_JCT="your_bili_jct"
export BILI_BUVID3="your_buvid3"
```

获取Cookie的方法：
1. 登录B站网页版
2. 按F12打开开发者工具
3. 在Application/存储 -> Cookies中找到上述三个值

## 技术栈

- [bilibili-api-python](https://github.com/Nemo2011/bilibili-api) - B站API Python封装
- requests - HTTP请求库
- json - JSON处理

## License

MIT

## 贡献

欢迎提交Issue和Pull Request！
