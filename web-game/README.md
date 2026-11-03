# 东周列国志 H5 战棋

可直接发布的静态网页游戏，包含 172 个原始 Lua 关卡、169 幅 WebP 战场地图和完整选章界面。

## 本地运行

请通过 HTTP 静态服务器打开目录，不能直接双击 `index.html`，因为浏览器需要读取关卡清单与 Lua 文件。

```powershell
python -m http.server 8765 --directory web-game
```

访问 `http://127.0.0.1:8765/`。

## 重新生成

在仓库根目录执行：

```powershell
node tools/export-web-campaign.js
python tools/convert-web-maps.py
node tools/verify-web-release.js
```

发布包需要保持 `index.html` 位于 ZIP 根目录。浏览器 Lua 运行时使用 Fengari，许可证见 `vendor/LICENSE`。

## 生成发布 ZIP

在仓库根目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build-h5-release.ps1
```

脚本会先执行发布门禁，再生成 `dongzhou-h5-release-final-YYYYMMDD.zip`。发布包只包含运行时引用的配音、地图、关卡和前端文件；配音生产计划、声线卡、QA 截图及未引用候选不会进入交付包。
