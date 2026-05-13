# 开发日志

## 2026-05-13

### Windows 版 v1.4.1：同步 mac 黑灰 UI、Logo 与路径显示修复

- 参考 mac 主仓库 `jiashusu/valorant-highlight-clipper` 的 AppKit UI，把 Windows PySide6 视觉从蓝黑电竞风调整为 Apple 黑灰玻璃风：
  - 背景使用 `#050506/#0B0B0D`，面板使用半透明 `#18181B`，输入框使用 `#0D0D10`，卡片使用 `#1D1D22`。
  - 只保留 `#64D2FF` 作为主按钮、作者链接和进度条强调色，降低大面积青色和蓝色描边。
  - 标题栏新增 `Windows v1.4.1 · 构建号`，方便确认当前运行版本。
- 同步 mac 更新日志里提示的 Windows 缺项：
  - 从 mac 图标资源生成 Windows 专用 `ValorantHighlightClipper.ico`。
  - exe、窗口、任务栏和标题栏左侧小图标使用专属 logo。
  - PyInstaller spec 接入图标资源。
- 修复视频列表路径显示 bug：
  - 路径列禁用省略显示，不再只显示 `C:...`。
  - 表格开启横向滚动，长路径可完整查看。
  - 每个路径单元格增加完整路径 tooltip，并继续在 `UserRole` 保存真实路径。
- 更新检查加入短版本兜底比较：
  - 当前版本和远端版本短版本一致时视为已是最新，避免“当前和最新一样仍提示新版”。

## 2026-05-13

### Windows 版 v1.4.0：PySide6 玻璃 UI 迁移

- 将 Windows 默认桌面入口从 Tkinter 切换到 PySide6：
  - 新增 `src/valorant_clipper/qt_app.py`。
  - `windows/launcher.py` 改为启动 PySide6 UI。
  - 保留 `src/valorant_clipper/desktop_app.py` 作为旧版参考/回退，不再作为 Windows 默认入口。
- 视觉系统升级为黑暗玻璃风：
  - 使用无边框自绘标题栏，保留拖动、最小化、最大化/还原、关闭。
  - Windows 11 下优先启用 Mica/System Backdrop，失败时使用深色渐变背景。
  - 面板、日志框、参数区、Highlights 卡片使用半透明背景、柔和描边、圆角和阴影。
  - 按钮统一为圆角玻璃质感，主按钮使用青色高亮，删除按钮使用暗红色层级。
  - 视频列表从旧 Treeview 视觉迁移为 Qt 暗色表格。
- 功能保持不变：
  - 文件夹/视频选择、递归扫描、参数设置、日志只读、开始剪辑、进度条、Highlights 卡片墙、低清预览、高清播放、删除、定位视频、检查更新全部保留。
  - `定位此视频` 继续只接受真实存在的导出 mp4，并通过 Windows Explorer 精确选中文件。
  - 中英文切换继续默认中文，不持久化语言选择。
  - 更新检查优先读取 GitHub 公开 Contents API，失败时再回退 raw `latest.json`，避免 raw 缓存导致仍显示旧版本。
- 打包与发布准备：
  - `requirements.txt` 增加 `PySide6>=6.7,<7`。
  - PyInstaller spec 移除 Tkinter/PIL.ImageTk 相关 hidden imports，加入 PySide6 QtCore/QtGui/QtWidgets。
  - 版本号更新为 `v1.4.0-windows`。

## 2026-05-12

### Windows 版 v1.3.2：自绘标题栏、语言切换和定位修复

- 修复“定位此视频”仍打开错误目录的问题：
  - 新增专用 `reveal_in_explorer`。
  - Windows 下改用 ShellExecute 调用资源管理器并传入 `/select,"完整路径"`。
  - 导出 mp4 不存在时弹窗显示真实路径，并写入日志。
- 去掉顶部白色系统标题栏：
  - 使用黑色自绘标题栏。
  - 保留拖动、最小化、最大化/还原和关闭。
  - 最大化时使用系统工作区，避免遮挡任务栏。
- 右上角新增：
  - `原作者: shu`，点击打开 Windows GitHub 仓库。
  - 中英文切换按钮，默认中文，不持久化。
- UI 继续升级为电竞工具风：
  - 移除明显复古边框，强化深色面板、深色卡片、青色主按钮和红色删除按钮。
  - Highlights 标题下新增提示，说明当前版本仍可能输出队友击杀片段，可先手动删除。

### Windows 版 v1.3.1：修复更新检查、文件定位和预览布局

- 修复“检查更新”在私有仓库下返回 HTTP 404 的问题：
  - 新增公开更新清单仓库，只存放 `latest.json`。
  - App 优先读取公开清单，不再依赖私有 release API。
  - 私有仓库仍保留源码和 exe 发布包。
- 修复“定位此视频”打开到错误目录的问题：
  - Windows Explorer 改用 `/select,"完整文件路径"` 格式。
  - 导出视频不存在时直接提示具体路径，不再错误打开“文档”目录。
- 调整窗口和右侧预览区域：
  - 默认窗口从 `1560x960` 调整为 `1720x980`。
  - 左右分栏从 `2:3` 调整为 `2:6`，右侧 Highlights 区域更宽。
  - 缩略图和卡片内预览从 `320x180` 提升到 `384x216`。

### 恢复 Windows 版源码并上传 GitHub

- 从原 macOS 源码仓库恢复项目结构。
- 新建 Windows 源码目录：`无畏契约自动剪辑-Windows源码`。
- 补齐 Windows 构建入口、PyInstaller 配置和构建脚本：
  - `windows/launcher.py`
  - `windows/ValorantHighlightClipper-windows.spec`
  - `windows/build_windows.ps1`
- 版本信息固定为 `v1.3.0-windows`，便于更新检查对比 GitHub Release。
- README 改为 Windows 源码说明，明确源码入口和重新打包方式。

## 2026-05-11

### Windows 版升级：黑色 UI、更新检查、预览质量和定位文件

- 用户反馈：
  - 默认窗口还需要更大。
  - 旧 UI 太像复古系统控件，希望改成黑色主题。
  - 检查更新需要修复。
  - 卡片内预览需要更流畅、更清晰。
  - 导出视频的“打开目录”要改为直接定位该视频文件。
  - 继续优化流程，不删除原有功能。

- 修改内容：
  - 默认窗口改为 `1560x960`，最小窗口改为 `1280x820`。
  - 使用 Tkinter `clam` 主题重做深色 UI：
    - 深色背景、深色面板、暗色卡片。
    - 高亮按钮、危险操作按钮、深色输入框、表格、日志和进度条。
  - 检查更新改为读取 Windows 版仓库最新 Release：
    - `jiashusu/valorant-highlight-clipper-windows`
    - 发现新版时打开 Windows Release 页面，不再跳 macOS Actions。
    - 私有仓库自动检查失败时，可以直接打开 Release 页面手动查看。
  - 卡片预览升级：
    - 缩略图和预览尺寸从 `260x146` 提升到 `320x180`。
    - 卡片内预览帧率从 `20fps` 提升到 `30fps`。
    - 预览帧和缩略图使用 Lanczos 缩放，JPEG 质量提升。
  - 每个导出片段按钮从“打开目录”改成“定位此视频”，Windows 下调用资源管理器直接选中 mp4。
  - 保留高画质导出、严格过滤队友击杀、不弹系统命令窗口、日志只读、高光卡片墙、卡片内预览、高清播放和删除功能。

### Bug 修复与底层优化

- 修复“已经选择视频仍提示请先扫描并选择一个视频”的问题：
  - 扫描完成后自动选中第一个视频。
  - 点击开始剪辑时如果列表里有视频，也会自动补选。
- 更严格过滤队友击杀：
  - UI 默认置信度提升到 `0.93`。
  - 开启严格过滤时核心识别至少使用 `0.94` 置信度。
  - 开启严格过滤时最短事件至少为 `0.75s`，减少短暂误识别。
- 导出质量提升：
  - 非快速无损模式使用 H.264 `slow` preset 和 `CRF 14`。
  - 视频像素格式使用 `yuv420p`。
  - 音频优先复制原音轨，失败时回退 AAC 192k。
- Windows 后台处理不再弹出系统命令窗口：
  - ffmpeg、ffprobe、ffplay 调用统一隐藏窗口。
- 处理日志改为只读：
  - 用户不能在日志框里输入。
  - 程序仍可正常写入进度日志。
- 高光卡片区域支持鼠标滚轮滚动：
  - 鼠标放在卡片、缩略图、按钮区域上也能滚动。

### 高光卡片墙

- 右侧导出区域改为 3 列高光卡片墙。
- 每张卡片包含：
  - 低清预览缩略图和播放三角。
  - `Highlight #序号`。
  - 约 N 杀、片段长度、开始和结束时间。
  - “高清播放”“定位此视频”“删除”按钮。
- 点击缩略图会在卡片内部播放轻量预览。
- “高清播放”使用内置 `ffplay` 播放真实导出的 mp4。

## 早期开发记录

- 从 macOS 版本迁移核心识别逻辑到 Windows。
- 使用 `valorant.npy` 和 `valorant-mask.png` 识别 Valorant 击杀信息区域。
- 支持选择单个视频或素材文件夹。
- 支持递归扫描。
- 支持扫描视频列表并显示时长、大小和路径。
- 支持按参数导出高光：
  - 置信度
  - 识别帧率
  - 提前秒数
  - 延后秒数
  - 合并间隔
  - 最短事件秒数
  - 最多分析秒数
- 修复 NumPy 打包兼容问题：
  - `requirements.txt` 固定为 `numpy>=1.26.0,<2.0`。
  - PyInstaller hidden import 加入 `numpy.core.multiarray`。
