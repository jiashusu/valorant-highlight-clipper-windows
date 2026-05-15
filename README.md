# Valorant 高光剪辑 Windows 版
<img width="1920" height="1032" alt="image" src="https://github.com/user-attachments/assets/ac8bbefc-017d-4471-bbd5-7db4e95a9368" />

这是 Windows 桌面版源码。程序会扫描 Valorant 录像，识别击杀信息区域，自动导出高光片段。当前发布包是纯桌面 exe，不打开浏览器，也不启动本地网页服务。

## 相关版本

- macOS 版仓库：[jiashusu/valorant-highlight-clipper](https://github.com/jiashusu/valorant-highlight-clipper)
- 如果你在 macOS 上使用，请下载 macOS 版；它使用原生 AppKit 桌面界面、macOS 专用 `.app` 打包流程和 GitHub Actions 更新入口。
- 本仓库只维护 Windows 版。两个版本会尽量同步核心剪辑体验，包括高光卡片、低清预览、高清播放、定位视频、删除片段和更新提示；但 UI、打包方式和更新检查入口会按系统分别维护。

## 主要入口

- Windows 桌面入口：`windows/launcher.py`
- PySide6 玻璃 UI：`src/valorant_clipper/qt_app.py`
- 旧 Tkinter 界面参考/回退：`src/valorant_clipper/desktop_app.py`
- 核心识别与导出：`src/valorant_clipper/core.py`
- 更新检查：`src/valorant_clipper/update_checker.py`
- Windows 打包配置：`windows/ValorantHighlightClipper-windows.spec`
- Windows 构建脚本：`windows/build_windows.ps1`

## 当前版本

- 发布版本：`v1.4.2-windows`
- 默认窗口：`1720x980`
- 主题：PySide6 黑灰玻璃 UI，参考 macOS AppKit 版 Apple 黑灰视觉；Windows 11 Mica 优先，失败时使用深色模拟玻璃背景
- 图标：使用专属 `ValorantHighlightClipper.ico`，覆盖 exe、窗口和任务栏图标
- 布局：保留左右工作区，左侧路径/参数/视频列表，右侧日志和 Highlights 卡片墙
- 提示：参数区标题会提醒不要随意改参数；开始剪辑前会在日志里显示粗略预计耗时
- 视频列表：长路径完整显示，支持横向滚动和完整路径 tooltip
- 高光卡片：3 列卡片墙，支持低清卡片内预览、高清播放、定位视频、删除片段
- 导出画质：H.264 `CRF 14`、`slow` preset，优先复制原音频，失败时回退 AAC 192k
- 预览质量：`384x216`、`30fps`、Lanczos 缩放
- 更新检查：读取公开更新清单，优先 GitHub Contents API，并支持短版本一致即最新
- 定位视频：使用 Windows Shell 精确选中导出的 mp4

## 使用源码运行

```powershell
cd "C:\Users\shusu\Documents\jiashu project\无畏契约自动剪辑-Windows源码"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe windows\launcher.py
```

本地运行和打包都需要 `ffmpeg`、`ffprobe`、`ffplay`。可以把三个 exe 放到项目的 `ffmpeg` 或 `vendor/ffmpeg` 目录，也可以安装到系统 PATH。

## 打包 exe

```powershell
cd "C:\Users\shusu\Documents\jiashu project\无畏契约自动剪辑-Windows源码"
.\windows\build_windows.ps1
```

构建完成后会生成：

```text
release\ValorantHighlightClipper.exe
```

也可以直接在 Windows 版仓库的 Releases 页面下载 `ValorantHighlightClipper.exe`。
