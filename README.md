# Bilibili 视频字幕提取工具

一个用于搜索B站视频并自动提取字幕的Python工具。

## 功能特性

- 搜索B站视频
- 通过BV号或URL获取视频信息
- 自动检测并提取视频字幕
- 支持多种字幕格式导出（SRT、JSON、TXT）
- 支持多语言字幕

## 安装

```bash
pip install -r requirements.txt
```

## 配置

首次使用需要配置B站cookies（用于访问字幕API）：

1. 登录 bilibili.com
2. 打开浏览器开发者工具 (F12)
3. 进入 Application/存储 -> Cookies
4. 复制以下cookie值：
   - `SESSDATA`
   - `bili_jct`
   - `buvid3`

5. 运行配置命令：
```bash
python main.py config
```

## 使用方法

### 搜索视频
```bash
python main.py search "关键词"
```

### 提取字幕（通过BV号）
```bash
python main.py extract BV1xx411c7mD
```

### 提取字幕（通过URL）
```bash
python main.py extract https://www.bilibili.com/video/BV1xx411c7mD
```

### 指定输出格式
```bash
python main.py extract BV1xx411c7mD --format srt
python main.py extract BV1xx411c7mD --format txt
```

## 输出

字幕文件将保存在 `subtitles/` 目录下，文件名格式：
```
{视频标题}_{BV号}_{语言}.{格式}
```

## 注意事项

- 只能提取有CC字幕的视频（UP主或B站官方提供的字幕）
- 无法提取硬字幕（嵌入视频画面中的字幕）
- 需要登录态的cookies才能访问字幕API
- cookies有效期约为1个月，过期需重新配置

## 技术说明

本工具使用B站官方API：
- 搜索API: `https://api.bilibili.com/x/web-interface/search/type`
- 视频信息API: `https://api.bilibili.com/x/web-interface/view`
- 字幕API: `https://api.bilibili.com/x/player/wbi/v2`

## License

MIT
