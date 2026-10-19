# 100个句子记完7000个雅思单词（H5版）

这是一个 **H5 网页项目**，可在手机和电脑浏览器中使用，无需安装原生 App。围绕“100个句子记完7000个雅思单词”的学习目标，通过句子精读、核心词表、主题归纳和词汇回顾，在语境中理解与记忆雅思词汇。

公开仓库提供 H5 界面与学习交互代码，附原创示例，支持自行导入有权使用的课程。项目名称说明学习目标，不代表公开仓库内已包含原书100句和7000个词，也不保证学习效果。

## 在线体验（无需下载）

**[点击打开 H5 在线预览](https://timedetective.github.io/100-sentences-7000-ielts-words-h5/)**

手机和电脑浏览器均可直接打开，无需下载、安装或注册。在线预览使用 3 个原创示例句，可体验句子精读、查词、核心词表、主题归纳、收藏与回顾。发音使用设备朗读，实际声音依浏览器和已安装音色而定。

GitHub Pages 由 `.github/workflows/pages.yml` 自动构建，仅发布原创示例和公开代码；更新 `main` 分支后会自动更新预览。自行导入的私人课程与音频不会被此工作流读取。

> **仅供爱好者非商业学习、研究与交流，禁止商业化。**
> 源码公开采用自定义非商业许可，不属于 OSI 定义的开源软件。使用、修改或分发前，请阅读 [LICENSE](LICENSE) 和 [免责声明](DISCLAIMER.md)。免责声明不替代第三方授权，也不排除依法不得排除的责任。

## 功能

- 句子阅读、译文与语法展开、目录检索及分段查看。
- 逐词查义、核心词表、可展开的主题归纳。
- 英美设备朗读；可接入自行准备且有权使用的自然语音和逐词时间轴。
- 收藏、按句词汇回顾、可选填空、自主标记读懂。
- localStorage 保存位置与学习记录，支持导出；不需要账号或后端。
- 播放状态局部更新，避免词义弹窗反复创建和闪动。

公开版只附 **3 个原创示例句及自编词义**，用于演示功能。仓库不包含商业书籍、原书完整课程、词典数据库、配套音频、学习记录、站点账号或部署凭据。

## 本地运行

需要 Python 3.9 或更高版本，无需安装前端依赖：

```sh
python3 tools/serve.py
```

打开 `http://127.0.0.1:8780/`。首次运行会从 `examples/course.demo.json` 生成被 Git 忽略的 `dist/course.js`。默认使用设备朗读；对应口音不可用时会提示。

只生成静态文件：

```sh
python3 tools/build_course.py
```

然后将 `dist/` 作为静态站点目录部署。站点内已包含使用声明，根目录文档通过构建步骤同步进 `dist/`。

## 使用自己的内容

仅导入你有权使用的内容，JSON 结构参照 `examples/course.demo.json`：

```sh
python3 tools/build_course.py --input private/course.json
python3 tools/serve.py --keep-course
```

课程可以是数组，或含 `lessons` 数组的对象。句子 ID 从 1 连续递增；词条 ID 需唯一；`glosses` 覆盖句中的英文词；`exerciseAnswer` 必须出现在原句中。构建工具会验证关键字段。

`private/`、生成的 `dist/course.js`、`dist/audio/`、本地环境文件和音频均默认忽略。不要用 `git add -f` 上传私人课程或第三方受限内容。

## 可选：生成自然语音

公开版无需语音服务密钥即可使用浏览器设备朗读。若要自行生成自然语音：

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install edge-tts mutagen
python tools/generate_narration.py
```

生成工具需要联网，会将当前课程文字发送到语音服务。运行前请确认内容可用于该服务，并遵守服务条款。生成内容不随本仓库提供，也不因本项目的许可而自动获得公开分发或商业使用权。保留生成结果在本地；不要提交生成后的语音索引。

## 项目结构

```text
dist/                   静态界面与播放器
examples/course.demo.json 原创示例课程
tools/build_course.py   验证并构建课程
tools/serve.py          本地开发服务器
tools/generate_narration.py 可选语音生成工具
LICENSE                非商业使用许可
DISCLAIMER.md          使用声明与责任范围
CONTRIBUTING.md         贡献说明
```

## 许可

允许个人非商业学习、研究、修改与交流；分享修改版须保留本许可、免责声明并标注修改。未经书面许可，禁止销售、付费课程、收费部署、广告变现、商业产品集成和商业业务使用。

本项目没有采用 MIT/Apache/GPL 许可。第三方内容、服务与依赖继续受其各自条款约束。关于“开源”与商业使用的定义，参见 [OSI 官方定义](https://opensource.org/osd)。
