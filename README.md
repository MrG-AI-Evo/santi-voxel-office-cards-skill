# 三体方块人职场梗卡 | Santi Voxel Office Cards

A Codex Skill for brainstorming Chinese *Three-Body*-inspired workplace satire and rendering selected ideas as separate voxel character cards.

一个先挑梗、再出图的 Codex Skill：把《三体》概念映射成冷面职场笑话，并将选中的角色各自排成一张白底方块人卡片。本项目是非官方同人创作工具，没有使用官方人物造型或标识。

## 功能 | What it does

1. 输入职场主题，先获得四个角色创意：三体概念、角色标题、简短说明、红色收梗。
2. 选择并修改文案后，Skill 为每个角色分别生成原创体素办公室场景。
3. 排版脚本把确认的中文文案写在白底上，分别导出 **1080×1440、不透明、无透明通道的 PNG**。上方场景约占 58%，下方文字约占 42%；每张卡片都是一个文件，不会拼图。

默认语气是一本正经的冷面讽刺。主题不限于节前工作，也可以是开会、汇报、绩效、带团队等职场情境。系列标题随主题变化。

The image model draws only the scenes. The bundled renderer places approved Chinese copy afterward, keeping typography clear and avoiding image-model text errors. Each card uses roughly 58% scene and 42% white typography area, matching the revised reference layout.

## 安装 | Install

把以下文字发给 Codex：

```text
请使用 $skill-installer 安装这个公开 GitHub 仓库中的 Skill：
仓库：https://github.com/MrG-AI-Evo/santi-voxel-office-cards-skill
路径：.
安装名：santi-voxel-office-cards
```

调用名：`$santi-voxel-office-cards`

## 使用 | Use

```text
用 $santi-voxel-office-cards，以“领导临下班开会”为主题，先想四个三体方块人职场梗，我选好文案后再分别出图。
```

选定创意后可以说：

```text
用第 1 和第 3 个，红句按我修改的版本来，每张分别输出 PNG。
```

The Skill can also render already approved copy directly when you explicitly ask it to do so.

## 要求与边界 | Requirements and boundaries

- 需要可用的图像生成能力，以及 Python 3 和 Pillow。Codex desktop 的工作区运行时通常提供 Pillow；其他环境可运行 `python -m pip install -r requirements.txt`。
- 仓库附带 Noto Sans CJK SC 常规和粗体，用于稳定的中文排版；字体遵循其单独的 [SIL Open Font License](assets/OFL-Noto-CJK.txt)。
- 画面使用原创方块人和办公场景，不复刻现成截图、官方角色或 Logo；仓库不包含用户参考截图。
- Skill 的使用遵循 [PolyForm Noncommercial License 1.0.0](LICENSE.md)，仅供非商用。请将使用本 Skill 制作的卡片也仅用于非商用。仓库许可不会自动取得网友独立生成图片的权利，也不能保证对每张产图的后续使用施加可执行限制；生成结果的权属还取决于相应服务条款及适用法律。

Search terms: 三体职场梗、方块人、体素角色卡、职场讽刺、Codex Skill; Three-Body workplace meme, voxel office card.
