# Valorant Highlight Clipper for Windows

一款本地运行的 Windows 桌面 App，用来扫描 VALORANT 录屏、识别击杀信息区域，并自动导出高光片段。

This is a local Windows desktop app that scans VALORANT recordings, detects kill-feed events, and exports highlight clips automatically.

<img width="1920" height="1032" alt="Valorant Highlight Clipper Windows screenshot" src="https://github.com/user-attachments/assets/ac8bbefc-017d-4471-bbd5-7db4e95a9368" />

> 非 Riot Games 官方项目。本工具只处理你本机的视频文件，不接入 Riot API，也不会修改游戏文件。
>
> This is not an official Riot Games project. It only processes local video files, does not use the Riot API, and does not modify game files.

## 中文说明

### 项目定位

`Valorant Highlight Clipper for Windows` 是给 Windows 用户使用的 VALORANT 高光剪辑工具。它会读取录屏中的击杀信息区域，按参数识别击杀事件，把前后几秒自动合并并导出为独立 mp4 片段。

它是纯桌面版：不打开浏览器，不启动本地网页服务，所有路径选择、扫描、剪辑、预览、删除、定位视频和更新检查都在 App 窗口里完成。

### 相关版本

- macOS 版仓库：[jiashusu/valorant-highlight-clipper](https://github.com/jiashusu/valorant-highlight-clipper)
- 如果你在 macOS 上使用，请下载 macOS 版；它使用原生 AppKit 桌面界面、macOS 专用 `.app` 打包流程和 GitHub Actions 更新入口。
- 本仓库只维护 Windows 版。两个版本会尽量同步核心剪辑体验，但 UI、打包方式和更新检查入口会按系统分别维护。

### 功能亮点

- PySide6 Windows 桌面界面，黑灰玻璃风，参考 macOS AppKit 版视觉。
- Windows 11 下优先启用 Mica / System Backdrop，失败时使用深色模拟玻璃背景。
- 无边框自绘标题栏，支持拖动、最小化、最大化/还原和关闭。
- 支持选择素材文件夹或单个视频文件。
- 支持递归扫描素材目录。
- 自动读取视频时长、大小和完整路径，长路径支持横向滚动和 tooltip。
- 自动识别击杀信息区域并导出高光片段。
- 每个导出片段显示约几杀、起止时间和片段长度。
- Highlights 三列卡片墙，适合快速筛选片段。
- 卡片内低清预览，不必每次打开完整播放器。
- 高清播放按钮调用内建 `ffplay.exe` 播放真实导出视频。
- Windows Explorer 精确定位导出的 mp4 文件。
- 支持删除误剪或不需要的片段。
- 严格过滤队友击杀选项，尽量降低误剪。
- 开始剪辑前显示粗略预计耗时。
- 中英文界面切换，默认中文。
- 自动检查 Windows 版新版本，并支持短版本一致即最新。
- exe、窗口、任务栏和标题栏左侧小图标使用专属 logo。

### 下载和使用

1. 在 GitHub Releases 下载最新版 `ValorantHighlightClipper.exe`。
2. 把 exe 放到你喜欢的位置并双击打开。
3. 准备你的录屏目录，默认建议放在：

```text
C:\Users\<你的用户名>\Videos\VALORANT_CLIPS
```

4. 在 App 中选择素材文件夹或单个视频。
5. 选择输出目录，默认会输出到程序运行目录下的：

```text
outputs\valorant_highlights
```

6. 点击“扫描视频”，确认列表里出现视频。
7. 点击“开始剪辑”，等待导出完成。
8. 在 Highlights 卡片墙中预览、高清播放、定位或删除片段。

### 参数建议

默认参数已经按当前测试视频调过，一般不建议随便改。特别是这些参数：

- `置信度`：越高越严格，误剪更少，但可能漏掉击杀。
- `识别帧率`：越高越细，但处理更慢。
- `提前秒数 / 延后秒数`：控制导出片段前后保留多久。
- `合并间隔`：相近击杀会合并到同一个片段。
- `最短事件秒`：过滤很短的误识别。
- `严格过滤队友击杀`：推荐开启。
- `快速无损截取`：速度更快，但兼容性和切点精度可能受视频编码影响。

### 从源码运行

环境要求：

- Windows 10 或 Windows 11
- Python 3.11 或 3.12
- `ffmpeg.exe`
- `ffprobe.exe`
- `ffplay.exe`

可以把三个 ffmpeg 工具放到项目的 `ffmpeg` 或 `vendor\ffmpeg` 目录，也可以安装到系统 PATH。

安装依赖并运行：

```powershell
cd "C:\Users\shusu\Documents\jiashu project\无畏契约自动剪辑-Windows源码"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe windows\launcher.py
```

如果你的素材目录不在默认位置，可以设置环境变量：

```powershell
$env:VALORANT_CLIPS_DIR = "D:\Videos\VALORANT_CLIPS"
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe windows\launcher.py
```

### 打包 Windows exe

打包前确认 `ffmpeg.exe`、`ffprobe.exe`、`ffplay.exe` 可以被构建脚本找到。打包脚本会把可用的 ffmpeg 工具和模型资源一起放进发布产物：

```powershell
.\windows\build_windows.ps1
```

构建完成后产物位于：

```text
release\ValorantHighlightClipper.exe
```

当前发布版本：

```text
v1.4.2-windows
```

### 项目结构

```text
src/valorant_clipper/core.py             核心识别、分组和导出逻辑
src/valorant_clipper/qt_app.py           Windows PySide6 桌面界面
src/valorant_clipper/desktop_app.py      旧 Tkinter 界面参考/回退
src/valorant_clipper/update_checker.py   Windows 更新检查
assets/valorant_clipper/                 击杀识别模型和遮罩资源
assets/app_icon/                         Windows 图标资源
windows/launcher.py                      Windows 桌面入口
windows/build_windows.ps1                Windows 打包脚本
windows/ValorantHighlightClipper-windows.spec PyInstaller 打包配置
```

### 已知限制

- 当前识别逻辑仍可能误剪到队友击杀，建议开启“严格过滤队友击杀”，并在导出后手动删除不需要的片段。
- 识别区域按常见 16:9 VALORANT 录屏布局设计，非标准分辨率、裁剪画面或特殊 HUD 可能影响结果。
- 第一次生成缩略图和低清预览会占用一些时间，后续会复用缓存。
- 如果系统、项目目录或 exe 旁边找不到 `ffmpeg.exe` / `ffprobe.exe` / `ffplay.exe`，扫描、导出或高清播放会失败。
- 当前仓库维护 Windows 版本；macOS 版本不在本仓库维护。

### 常见问题

**为什么没有识别到片段？**

可以尝试降低置信度、缩短最短事件秒数，或确认视频中击杀信息区域没有被遮挡、裁剪或压缩得太严重。

**为什么会剪到队友击杀？**

击杀信息区域本身比较小，且不同录屏压缩质量差别很大。当前版本已经有严格过滤选项，但仍不能保证 100% 排除队友击杀。

**为什么播放高清版需要 ffplay？**

App 使用随包携带或系统 PATH 中的 `ffplay.exe` 播放真实导出的 mp4，这样比在 UI 里手写播放器更稳定。

**更新检查去哪里下载新版？**

Windows 版会读取公开更新清单，并打开 `jiashusu/valorant-highlight-clipper-windows` 的 Releases 页面下载新版 exe。

## English

### Overview

`Valorant Highlight Clipper for Windows` is a local desktop app for turning VALORANT recordings into highlight clips. It scans the kill-feed area in each video, detects kill events, merges nearby events, and exports short mp4 clips around those moments.

The app is fully desktop-native. It does not open a browser or start a local web server. File selection, scanning, clipping, previewing, deletion, reveal-in-Explorer, and update checks all happen inside the app window.

### Related Version

- macOS repository: [jiashusu/valorant-highlight-clipper](https://github.com/jiashusu/valorant-highlight-clipper)
- If you use macOS, download the macOS version. It uses a native AppKit desktop UI, macOS-specific `.app` packaging, and a GitHub Actions update flow.
- This repository maintains the Windows version only. The two versions aim to share the same clipping workflow, while UI, packaging, and update checks are maintained separately for each platform.

### Features

- PySide6 Windows desktop UI with a dark gray glass design inspired by the macOS AppKit version.
- Windows 11 Mica / System Backdrop when available, with a dark fallback background.
- Custom borderless title bar with drag, minimize, maximize/restore, and close controls.
- Select a source folder or a single video file.
- Optional recursive folder scanning.
- Video list with duration, size, full path, horizontal scrolling, and tooltips.
- Kill-feed detection and automatic highlight export.
- Estimated kill count, start time, end time, and duration for each clip.
- Three-column Highlights card grid for quick review.
- Low-quality preview inside each card.
- HD playback through bundled or system `ffplay.exe`.
- Reveal exported mp4 files directly in Windows Explorer.
- Delete unwanted clips from the app.
- Strict own-kill filtering to reduce teammate-kill false positives.
- Rough time estimate before clipping starts.
- Chinese / English UI toggle.
- Windows update checks through the public update manifest and GitHub Releases.
- Dedicated icon for the exe, window, taskbar, and title bar.

### Quick Start

1. Download the latest `ValorantHighlightClipper.exe` from GitHub Releases.
2. Put the exe wherever you like and double-click it.
3. Prepare your recordings folder. The recommended default is:

```text
C:\Users\<your-user>\Videos\VALORANT_CLIPS
```

4. Choose a source folder or a single video in the app.
5. Choose an output folder. By default, clips are written under:

```text
outputs\valorant_highlights
```

6. Click `Scan Videos`.
7. Select a video and click `Start Clipping`.
8. Review the exported clips in the Highlights grid.

### Settings

The default settings are tuned for the current workflow and usually should not be changed unless you know what each option means.

- `Confidence`: Higher means stricter detection, fewer false positives, but more missed kills.
- `Scan FPS`: Higher is more detailed but slower.
- `Before / After seconds`: Extra time included before and after each detected event.
- `Merge gap`: Nearby kills are merged into one clip.
- `Min event sec`: Filters very short false detections.
- `Strict own-kill filter`: Recommended.
- `Fast stream copy`: Faster export, but exact cut accuracy and compatibility depend on the source video encoding.

### Run from Source

Requirements:

- Windows 10 or Windows 11
- Python 3.11 or 3.12
- `ffmpeg.exe`
- `ffprobe.exe`
- `ffplay.exe`

The ffmpeg tools can be placed in the project `ffmpeg` or `vendor\ffmpeg` directory, or installed into your system PATH.

Install dependencies and run:

```powershell
cd "C:\Users\shusu\Documents\jiashu project\无畏契约自动剪辑-Windows源码"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe windows\launcher.py
```

To override the default recordings folder:

```powershell
$env:VALORANT_CLIPS_DIR = "D:\Videos\VALORANT_CLIPS"
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe windows\launcher.py
```

### Build the Windows exe

Make sure `ffmpeg.exe`, `ffprobe.exe`, and `ffplay.exe` can be found by the build script. Available ffmpeg tools and model assets are bundled into the release output:

```powershell
.\windows\build_windows.ps1
```

Output:

```text
release\ValorantHighlightClipper.exe
```

Current release version:

```text
v1.4.2-windows
```

### Project Layout

```text
src/valorant_clipper/core.py             Detection, grouping, and export logic
src/valorant_clipper/qt_app.py           Windows PySide6 desktop UI
src/valorant_clipper/desktop_app.py      Legacy Tkinter UI reference/fallback
src/valorant_clipper/update_checker.py   Windows update checker
assets/valorant_clipper/                 Kill-feed model and mask assets
assets/app_icon/                         Windows icon resources
windows/launcher.py                      Windows desktop entrypoint
windows/build_windows.ps1                Windows build script
windows/ValorantHighlightClipper-windows.spec PyInstaller spec
```

### Notes and Limitations

- The detector may still export teammate kills. Keep `Strict own-kill filter` enabled and manually delete unwanted clips after export.
- The kill-feed crop is designed around common 16:9 VALORANT recordings. Non-standard layouts, cropped videos, or heavily compressed footage may reduce accuracy.
- The first thumbnail or low-preview generation can take a moment; cached previews are reused afterward.
- Scanning, exporting, and HD playback require `ffmpeg.exe`, `ffprobe.exe`, and `ffplay.exe`.
- This repository maintains the Windows version. The macOS version is not maintained here.

### Troubleshooting

**No clips were detected.**

Try lowering confidence, lowering the minimum event length, or checking whether the kill-feed area is visible and not heavily compressed.

**The app exported teammate kills.**

The kill-feed region is small and recording quality varies a lot. Strict filtering reduces false positives, but it cannot guarantee perfect results yet.

**HD playback does not start.**

Make sure `ffplay.exe` is bundled next to the app or available in your system PATH.

**Where does the update checker download from?**

The Windows app reads the public update manifest and opens the Releases page for `jiashusu/valorant-highlight-clipper-windows` when a newer exe is available.

### License and Credits

This project is a personal utility built for local highlight clipping. VALORANT and Riot Games are trademarks or registered trademarks of Riot Games, Inc. This project is not affiliated with or endorsed by Riot Games.
