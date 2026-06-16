---
name: baoyu-image-generation
description: "Baoyu image generation suite: article illustrations, comics, and infographics with Type × Style × Palette consistency. Unified workflow for all Baoyu output formats."
version: 1.0.0
author: JimLiu (宝玉)
license: MIT
tags: [baoyu, image-generation, illustration, comics, infographic, chinese]
category: creative
---

# Baoyu Image Generation Umbrella

This umbrella skill covers the Baoyu family of image generation tools for creating consistent visual content. Baoyu provides **Type × Style × Palette** consistency across all output formats.

## Output Format Selection

| Skill | Best For | Output | Use Case |
|-------|----------|--------|----------|
| **baoyu-article-illustrator** | Articles, blogs, docs | PNG illustrations | Content enhancement |
| **baoyu-comic** | Educational, biography, tutorials | Comic strips | Storytelling |
| **baoyu-infographic** | Data, metrics, technical | Info graphics | Data visualization |

## Core Principles

- **Visualize concepts, not metaphors** — if the article uses a metaphor (e.g., "电锯切西瓜"), illustrate the underlying concept, not the literal image.
- **Labels use source data** — actual numbers, terms, and quotes from the source content, not generic placeholders.
- **Prompt files are reproducibility records** — every generated output must have a saved prompt file before any image is created.
- **Strip secrets** — scan source content for API keys, tokens, or credentials before writing anything to disk.

## Three Dimensions

| Dimension | Controls | Examples |
|-----------|----------|----------|
| **Type** | Information structure | infographic, scene, flowchart, comparison, framework, timeline |
| **Style** | Rendering approach | notion, warm, minimal, blueprint, watercolor, elegant |
| **Palette** | Color scheme | macaron, warm, neon — overrides style's default colors |

Combine freely: `type=infographic, style=vector-illustration, palette=macaron`.

Or use presets: `edu-visual` → type + style + palette in one shot.

---

## Section: baoyu-article-illustrator (Article Illustrations)

Comprehensive guidance for generating PNG illustrations for articles and documents.

### When to Use

Trigger this skill when:
- The user asks to illustrate an article
- Add images to an article
- Generate illustrations for content
- Uses phrases like "为文章配图", "illustrate article", or "add images"

### Types

| Type | Best For |
|------|----------|
| `infographic` | Data, metrics, technical |
| `scene` | Narratives, emotional |
| `flowchart` | Processes, workflows |
| `comparison` | Side-by-side, options |
| `framework` | Models, architecture |
| `timeline` | History, evolution |

### Styles

See `references/styles.md` for Core Styles, the full gallery, and Type × Style compatibility.

### Output Structure

```
{output-dir}/
├── source-{slug}.{ext}    # Only for pasted content
├── outline.md
├── prompts/
│   └── NN-{type}-{slug}.md
└── NN-{type}-{slug}.png
```

**Default output directory:**

| Input | Output Directory |
|-------|------------------|
| Article file path | `{article-dir}/imgs/` |
| Pasted content | `illustrations/{topic-slug}/` (cwd) |

### Workflow

```
- [ ] Step 1: Detect reference images (if provided)
- [ ] Step 2: Analyze content
- [ ] Step 3: Confirm settings (clarify tool, one question at a time)
- [ ] Step 4: Generate outline → `outline.md`
- [ ] Step 5: Generate prompts (BLOCKING: every illustration must have a saved prompt file)
- [ ] Step 6: Generate images (image_generate)
- [ ] Step 7: Finalize
```

### References

- `references/article-illustrator-guide.md` — Complete article illustration guide
- `references/styles.md` — Style gallery + Palette gallery
- `references/workflow.md` — Detailed procedures
- `references/prompt-construction.md` — Prompt templates

---

## Section: baoyu-comic (Knowledge Comics)

Comprehensive guidance for generating educational comic strips and visual storytelling.

### When to Use

Use for:
- Educational content
- Biography storytelling
- Tutorial visualizations
- Knowledge sharing

### Output

Comic strips with consistent character styles and visual progression.

### References

See `references/comic-guide.md` for complete comic generation guidance.

---

## Section: baoyu-infographic (Data Visualization)

Comprehensive guidance for creating infographics and data visualizations.

### When to Use

Use for:
- Data visualization
- Metrics display
- Technical diagrams
- Process flows

### Output

High-impact infographics with clear data presentation.

### References

See `references/infographic-guide.md` for complete infographic generation guidance.

---

## Section: Common References

### Workflow

Detailed procedures for all Baoyu operations:
- `references/workflow.md` — Core workflow procedures
- `references/usage.md` — Invocation examples
- `references/prompt-construction.md` — Prompt templates and construction

### Styles and Palettes

- `references/styles.md` — Full style gallery with Type × Style compatibility
- `references/style-presets.md` — Preset shortcuts (type + style + palette combinations)

---

## Section: Platform Notes

| Platform | Notes |
|----------|-------|
| macOS | Uses `memo` CLI for Apple Notes integration |
| Linux | Standard CLI operation |
| Windows | Requires WSL or native support |

---

## Section: Related Skills

- `comfyui` — Node-based image generation with custom workflows
- `popular-web-designs` — Design system inspiration
- `sketch` — Quick design mockups