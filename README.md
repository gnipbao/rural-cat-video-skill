# 田园猫咪短片 Skill

把写实双猫做饭短片的制作流程封装成一个可复用的 Codex Skill：从选题、角色母图和世界设定，走到分镜、Renoise 视频生成、字幕剪辑和成片验收。

这套方法来自一次完整制作中的实际问题：猫一直认真做饭会平淡，冲突需要可见起因；角色稳定了，道具和食物仍可能跨镜改变。Skill 把这些问题转成可以反复使用的步骤。

## 它会做什么

- 用拨弄、追绳、踩奶等猫本能推动剧情，让两只猫都有本事，也都会失手。
- 先锁角色身份，再记录小院、道具和食物状态，减少续拍漂移。
- 区分角色母图、可选单镜首帧和生成后抽帧。
- 查询当前 Renoise 能力与报价，登记引用、跟踪同一任务，按已有授权推进。
- 在本地添加步骤字幕，检查动作因果、接触、声音与视频参数。

默认工具链是 **Codex 客户端 + 客户端内置生图 + Renoise MCP + 本地后期**。用户已选择其他可用工具时，可保留制作方法并按实际能力调整。

## 安装

技能目录是 `skills/rural-cat-video`。下载 ZIP 后把这个完整目录复制到自己的 Codex skills 目录，或在终端执行：

```bash
git clone https://github.com/gnipbao/rural-cat-video-skill.git
cd rural-cat-video-skill

skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
skill_target="$skill_root/rural-cat-video"
mkdir -p "$skill_root"
if [ -e "$skill_target" ]; then
  printf '%s\n' "已存在：$skill_target。请先比较内容，未覆盖。"
else
  cp -R skills/rural-cat-video "$skill_target"
fi
```

重新打开或刷新 Codex 会话后，用 `$rural-cat-video` 调用。若客户端未自动发现，直接提供该目录中 `SKILL.md` 的路径。

## 开始一集

```text
用 $rural-cat-video 做一条60秒、9:16的写实田园双猫做饭短片。
主题是秋天做红薯饼：一只橘猫好奇手欠，搭档认真但也爱追绳。
我希望有清楚的工序、两次转折和暖一点的结尾。
先完成选题、角色与分镜，再查可用模型和实际报价。
角色图用客户端内置生图，视频用 Renoise MCP，字幕在本地后期添加。
把文件保存在我指定的项目目录。
```

已有样片可这样继续：

```text
用 $rural-cat-video 继续这个项目。
读取已确认的角色、分镜和生成记录，保留前半段，只补剩余故事。
沿用已授权预算；先查原任务是否完成，避免重复提交。
重点检查面团颜色、两猫站位和结尾篮子与开场是否一致。
```

## 字幕小工具

`build_srt.py` 把秒制步骤时轴转成 SRT，只需 Python 标准库。复制示例 JSON 后，按自己成片的真实切点修改；这份示例不是历史项目的原始字幕。

```bash
python3 skills/rural-cat-video/scripts/build_srt.py \
  skills/rural-cat-video/assets/captions.example.json \
  --output ./captions.srt
```

输入结构为 `duration` 和 `captions` 数组；每条字幕含 `start`、`end`、`text`。脚本检查时长、顺序、重叠和毫秒舍入，默认拒绝覆盖，明确需要替换时使用 `--force`。它只生成字幕文件，不把字幕烧录进视频。

## 使用条件

- 客户端需要可用的生图能力和已连接的 Renoise MCP；本仓库不提供模型、账号或服务额度。
- 本地视频后期需要 Python、ffmpeg 和 ffprobe。具体字幕方案可能还需要 Pillow、字幕滤镜和中文字体。
- 图像在客户端生成并保存到本地，不意味着离线推理，也不意味着使用某个未返回的指定模型版本。
- 模型、引用方式、时长限制、价格和任务查询方式都在执行时读取，不把案例参数写死。
- Skill 是给助手的制作流程，不是自动下载凭据、批量扣费或直接发布视频的程序。

## 文件

```text
skills/rural-cat-video/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── character-world.md
│   └── shot-generation.md
├── assets/captions.example.json
└── scripts/build_srt.py
```

`SKILL.md` 是完整入口；两个参考文件分别提供角色/世界卡和分镜/生成模板，执行到对应步骤再读取。

## 许可

本仓库的原创流程文本与代码采用 [MIT License](LICENSE)。仓库不包含账号凭据、实际素材编号、私有项目数据、原始视频或第三方品牌资料。

这是独立制作流程项目，不代表所提及工具或平台的官方产品。生成结果与使用的素材按各自来源和服务条款处理。
