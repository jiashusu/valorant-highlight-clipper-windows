# Valorant 高光剪辑 Windows 纯桌面版

这是 Windows 纯桌面应用版本，不打开浏览器，不启动本地网页服务。所有操作都在应用窗口里完成。

## 下载

请在本仓库的 Releases 页面下载：

```text
ValorantHighlightClipper.exe
```

exe 已内置识别资源、`ffmpeg.exe` 和 `ffprobe.exe`，下载后可直接双击运行。

## 功能

- 选择素材文件夹或单个视频
- 扫描视频列表
- 扫描后自动选中列表里的第一个视频
- 设置识别参数
- 后台剪辑并显示进度日志
- 显示每个导出片段的估算击杀数
- 打开输出目录或选中片段所在目录
- 默认开启“严格过滤队友击杀”，减少误剪

## 使用方法

1. 双击 `ValorantHighlightClipper.exe`。
2. 在窗口里选择素材文件夹或单个视频。
3. 点击“扫描视频”，程序会自动选中列表里的第一个视频。
4. 按需要调整参数，然后点击“开始剪辑”。
5. 输出默认写到 exe 同目录下的 `outputs\valorant_highlights`。

## 版本说明

这是从 macOS 纯桌面版迁移出来的 Windows 独立版本。Windows 版仓库只放发布说明和下载入口，完整可执行文件通过 GitHub Release 分发。
