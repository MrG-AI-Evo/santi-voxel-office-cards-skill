---
name: santi-voxel-office-cards
description: Create original Chinese Three-Body-inspired voxel office satire cards. Use when a user wants to brainstorm workplace character jokes, select ideas, and turn each selected idea into a separate white-background 3:4 PNG.
---

# 三体方块人职场梗卡

Make original fan-style office humor cards that map recognizable *Three-Body* concepts to ordinary workplace power dynamics. The default voice is deadpan satire: an earnest explanation followed by a sharper red punchline. This is an unofficial fan creation workflow, not a source for official characters or branding.

## Work from the user's stage

1. If the user supplies a workplace theme but has not chosen copy, propose four distinct concepts. For each, show a character title, a two-to-three-line setup, a red punchline, and the specific *Three-Body* concept being mapped. Generate a short series heading from the theme. Invite selection or edits; wait for that selection before making cards. If the user has already approved copy or explicitly asks to render selected concepts, proceed with those concepts.
2. Preserve the user's chosen words and humor intensity. When no tone is given, use cool, matter-of-fact satire about fictional bosses, supervisors, office hierarchy, and workers. Keep the literary analogy understandable on first read. Avoid gratuitous hostility, real-person caricatures, and claims of official affiliation.
3. For each selected card, generate **one separate** original voxel office scene with the built-in image generation tool. The scene is only artwork: no typography, captions, signs, screen words, logos, watermarks, existing character designs, or copied reference-image composition. Ask for a clean white setting, a near-square or 4:3 composition with all important faces and objects inside the central crop-safe area, and a concrete visual action that matches that card alone. The renderer crops this scene to a 1080×840 window. Do not ask image generation to render Chinese card copy.
4. Save each scene file, then prepare a JSON spec for `scripts/render_card.py`: one series heading and one entry per card with `id`, `title`, `body`, `punchline`, and `scene_image`. Pass only approved copy. Add `\n` in long `body` or `punchline` strings at semantic pauses when needed; this controls line breaks without changing words. Render into a user-facing output directory. The renderer produces independent opaque 1080×1440 PNGs. Deliver only the PNGs unless the user asks for working files.
5. Inspect each finished image at full size against any layout reference supplied by the user. Check the scene-to-copy ratio, that the scene matches its concept, no important face or object is cropped, no source-image text or logo slipped in, the title/body/punchline exactly match approved copy, nothing is clipped, the lower text area is white, and files have no alpha channel. If the scene is wrong, regenerate or recrop that scene and render that card again. If copy is wrong, correct the spec and render again. Never use a collage to stand in for separate cards.

## Card contract

- Canvas: 1080×1440 pixels (3:4), opaque RGB white.
- Scene: top 840 pixels (58.3%); original blocky/voxel 3D office illustration, no embedded words.
- Typography: lower 600 pixels (41.7%) on white, generous left and right margins; black series heading, bold black character title, black setup, bold red final line. Keep copy concise enough for readable type. If the user provides a reference layout, match its visual hierarchy before delivery.
- Series title: adapt it to the user's theme; do not freeze it to a holiday series.
- `id`: unique lowercase ASCII slug with letters, digits, or hyphens. The output is `<id>.png`.

Example spec (paths are placeholders to replace with real scene files):

```json
{
  "series_title": "三体打工人节前生存指南",
  "cards": [
    {
      "id": "mianbizhe",
      "title": "这是 节前面壁者",
      "body": "表面上还在制定宏大计划，实际上把做不完的事统统列入‘长期战略’。",
      "punchline": "只要没人看见我的进度，就没人知道我延期了。",
      "scene_image": "/absolute/path/to/mianbizhe-scene.png"
    }
  ]
}
```

Run:

```bash
python scripts/render_card.py --spec /absolute/path/to/cards.json --output-dir /absolute/path/to/outputs
```

Use a Python environment with Pillow. In Codex desktop, `load_workspace_dependencies` can locate its bundled Python runtime. The renderer uses the bundled Noto Sans CJK SC fonts; their separate OFL notice is in `assets/OFL-Noto-CJK.txt`.

## Distribution and use

The Skill is offered under PolyForm Noncommercial 1.0.0. Tell users it is for noncommercial card making and request noncommercial use of cards produced with it. Do not claim that the Skill license automatically gives the Skill author rights in every independently generated output or guarantees enforcement of output restrictions. Do not place license notes, AI process notes, or source-review labels on the audience-facing cards.
