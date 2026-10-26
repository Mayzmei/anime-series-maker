<div align="center">

# Anime Series Maker · AI 番剧连载

**2 张角色设定图 + 1 句剧情 → 一集完整的动漫短片。然后同一批角色，接着拍下一集。**
爆点构思、逐秒分镜脚本、带配音的动画片段、质检、剪辑、Instagram 安全区封面和文案，全部交给你的 AI Agent。

[English](README.md) · **简体中文**

[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)
![Agent Skill](https://img.shields.io/badge/Agent%20Skill-SKILL.md-orange)
![Renoise MCP](https://img.shields.io/badge/video-Renoise%20MCP-ff7a1a)

<img src="docs/images/cover.jpg" width="820" alt="同一部 AI 番剧的四集画面">

</div>

> 我在 Instagram 连载一部 AI 同人番剧：40 多集，固定角色，最高单集 **60.5 万 / 49.5 万 / 30.1 万播放**。
> 这个仓库就是我的完整工作流，连同一路上烧积分踩过的所有坑，打包成一个 Skill。

---

## 效果

<!-- TODO: 换成 docs/gifs/ 里的 GIF + 视频链接 -->
| | | |
|:---:|:---:|:---:|
| **吓人失败只撑 3 秒** · 14 秒 · 60.5 万播放 | **变成猫娘** · 63 秒 · 49.5 万播放 | **口头禅三连** · 72 秒 · 30.1 万播放 |

---

## 它能做什么

- **是「剧集设定」，不是一次性 prompt**：角色、画风、声线、场景、固定梗都存在 `series.json` 里，第 30 集和第 1 集是同一批人。
- **先定爆点**：写剧本之前，Agent 先给 3 个一句话梗、推荐其中 1 个。依据是按真实播放量排出来的公式：吓人失败、变身、口头禅三连、想要又不肯说……
- **逐秒分镜**：每段 ≤15 秒，每个镜头都写清动作、符合人设的台词、音效和运镜，再拼成结构化的长 prompt。每段都会把角色的所有外观细节重写一遍，头发和衣服就不会跑偏。
- **花积分前先校验**：`build_prompt.py` 遇到缺设定图 ID、残留占位符、镜头缺运镜、时间对不上，会直接拒绝生成。
- **报价把关**：先报「几段 · 多少秒 · 多少积分 · 余额」，等你说「好」，先出第 1 段给你看，没问题再批量生成。
- **逐段质检**：对照设定图检查角色、检查有没有烧进去的字幕、检查声音性别和语言、检查剧情逻辑。不合格就整段重生成，不做局部拼补。
- **剪出来 IG 不吞片段**：所有片段统一格式后一次性编码（用 `-c copy` 直接拼 AI 片段会被 IG 吞掉一段）。导出 1080p，可选铺 BGM、加水印，响度统一到 −14 LUFS，并输出每个接缝的检查图。
- **封面 + 文案**：封面用设定图当参考，脸和人设对得上。画布 9:16，标题放在 IG 主页 3:4 裁切的安全区内，附裁切预览。文案用真正带来流量的钩子格式。
- **按你的数据进化**：每集都会记录，告诉 Agent 播放量，下一集的选题就按真实数据排序。

## 安装

```bash
git clone https://github.com/<YOUR_GITHUB>/anime-series-maker.git
mkdir -p ~/.claude/skills && cp -R anime-series-maker/skills/anime-series-maker ~/.claude/skills/   # Claude Code
mkdir -p ~/.codex/skills  && cp -R anime-series-maker/skills/anime-series-maker ~/.codex/skills/    # Codex
```

WorkBuddy、OpenClaw、豆包、千问、纳米Work 等支持 Skill 的产品：把 `skills/anime-series-maker` 文件夹（或打成 zip）导入 Skills 页面。

**连接 Renoise**（视频/图片生成，在浏览器里登录，不用填 API Key）：

| Agent | 方法 |
|---|---|
| Claude Code | `/plugin marketplace add ArcoCodes/renoise-plugins-official`，然后 `/plugin install renoise@renoise-plugins-official` |
| Codex | `codex mcp add renoise --url https://renoise.ai/api/public/mcp`，然后 `codex mcp login renoise` |
| Claude 桌面版 / claude.ai | 设置 → Connectors → 添加自定义连接器 → `https://renoise.ai/api/public/mcp` |
| 其他（Cursor、WorkBuddy、豆包、千问…） | 添加远程 MCP 服务器 `https://renoise.ai/api/public/mcp` |

最新说明见 [renoise.ai/plugin](https://renoise.ai/plugin)。装好后对 Agent 说「查一下我的 Renoise 余额」测试一下。

**本地工具**：`brew install ffmpeg`，`python3 -m pip install pillow`（只有封面检查要用）。

## 怎么用

> 用这两张角色设定图做一部番剧：她是傲娇大小姐，他很淡定、爱逗她。日语配音，柔和水彩画风。

> 下一集，来个她变成猫的。

Agent 会一次问完需要的信息，给你看剧本和积分报价，你说「好」之前一分钱都不花。

## 注意

- **请使用你有权使用的角色**，原创角色最安全。prompt 里只描述外观，不写作品名或角色名。
- 生成用的是你自己的 Renoise 积分，每次都会先报价。
- 按平台要求标注 AI 生成内容。

## License

MIT
