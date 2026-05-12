# Valorant 高光剪辑 Windows 版

这是 Windows 桌面版源码。程序会扫描 Valorant 录像，识别击杀信息区域，自动导出高光片段。当前发布包是纯桌面 exe，不打开浏览器，也不启动本地网页服务。

## 主要入口

- Windows 桌面入口：`windows/launcher.py`
- 核心识别与导出：`src/valorant_clipper/core.py`
- Tkinter 桌面界面：`src/valorant_clipper/desktop_app.py`
- 更新检查：`src/valorant_clipper/update_checker.py`
- Windows 打包配置：`windows/ValorantHighlightClipper-windows.spec`
- Windows 构建脚本：`windows/build_windows.ps1`

## 当前版本

- 发布版本：`v1.3.1-windows`
- 默认窗口：`1720x980`
- 主题：黑色 Windows 桌面 UI
- 高光卡片：3 列卡片墙，支持低清卡片内预览、高清播放、定位视频、删除片段
- 导出画质：H.264 `CRF 14`、`slow` preset，优先复制原音频，失败时回退 AAC 192k
- 预览质量：`384x216`、`30fps`、Lanczos 缩放
- 更新检查：读取公开更新清单，避免私有仓库 API 返回 404

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

## 使用发布版

也可以直接在 Windows 版仓库的 Releases 页面下载 `ValorantHighlightClipper.exe`。
