# 使用示例

## 方法1: 通过BV号提取字幕（推荐）

```bash
# 示例: 提取某个视频的字幕
python main.py --bvid BV1xx411c7mD

# 指定输出目录
python main.py --bvid BV1xx411c7mD --output ./subtitles
```

## 方法2: 通过URL提取字幕

```bash
python main.py --url "https://www.bilibili.com/video/BV1xx411c7mD"
```

## 方法3: 搜索视频

```bash
# 搜索视频（可能需要登录凭证）
python main.py --search "Python教程"
```

## 如何获取BV号

1. 打开B站视频页面
2. 查看URL地址栏
3. 找到类似 `BV1xx411c7mD` 的字符串
4. 完整URL示例: `https://www.bilibili.com/video/BV1xx411c7mD`

## 输出文件格式

程序会自动生成三种格式的字幕文件:

- `{BV号}_{语言}.json` - JSON格式（含时间轴）
- `{BV号}_{语言}.srt` - SRT字幕格式
- `{BV号}_{语言}.txt` - 纯文本格式

## 注意事项

⚠️ **只能提取UP主上传的字幕**
- 有些视频有UP主上传的字幕
- 有些视频只有AI自动生成的字幕（目前不支持）
- 有些视频没有任何字幕

## 使用Cookie登录（可选）

如果需要访问需要登录的视频，可以配置Cookie:

```bash
python main.py --bvid BV1xx411c7mD \
  --sessdata "your_sessdata" \
  --bili-jct "your_bili_jct" \
  --buvid3 "your_buvid3"
```

或使用环境变量:

```bash
export BILI_SESSDATA="your_sessdata"
export BILI_JCT="your_bili_jct"
export BILI_BUVID3="your_buvid3"

python main.py --bvid BV1xx411c7mD
```
