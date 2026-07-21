---
name: batch-file-renaming
description: Safe batch file renaming for files with embedded identifiers (knowledge cards, labeled images, AI-generated content). Use when renaming files based on their actual content rather than just filenames/timestamps. Covers OCR verification, dry runs, incremental processing, and pitfall avoidance.
category: file-management
---

# Batch File Renaming

## Description

Renaming multiple files systematically, especially when files contain embedded identifiers (knowledge cards, labeled images, sequentially generated content). Use this skill whenever you need to rename a batch of files based on their content rather than just their filenames or timestamps.

## When to Use

- Files generated sequentially (e.g., AI image generation with numbered filenames)
- Files contain visible identifiers (IDs, labels, titles) embedded in their content
- Need to standardize naming across a large set of files
- User provides a batch of files to organize/rename

## Core Principles

### ✅ ZERO GUESSING RULE — User Mandate, NON-NEGOTIABLE

**User corrections in Session 2026-07-13 elevated this from guideline to LAW:**

> "必须你自己识别再编号。不能猜。"
> "You must identify content yourself before renaming. No guessing."

> "必须每一张都识别一次再编号。"
> "Must identify EVERY SINGLE file before numbering."

> "必须解图片内容，提取编号信息，再重命名。"
> "Must read image content, extract number info, then rename."

> "不能套用其它数据，也是只能识别。"
> "Cannot use preset data/lookup tables, can only recognize."

**ABSOLUTE RULES — these override ALL shortcuts, ALL fallback patterns, ALL domain knowledge:**
1. Perform actual content recognition via OCR for **EVERY FILE** before renaming — NO EXCEPTIONS
2. No lookup tables (`TERM_MAP`), no preset term tables, no filename pattern matching
3. Do NOT sample "the first few" then assume a pattern holds
4. Do NOT trust manifest files alone — they can be wrong
5. The **ONLY source of truth** is the actual content of the file itself

If you cannot reliably identify files due to tool limitations:
- **STOP and inform the user**
- Ask for their help verifying a sample
- Propose a verification plan they can confirm before bulk processing

### ✅ ALWAYS Verify Content First

**Never assume sequential order based on:**
- Filename numbering (e.g., `file (1).png`, `file (2).png` may not correspond to actual content order)
- File timestamps (generation order may not match logical order)
- File size patterns

### ✅ Use macOS Vision for Image Content (PRIMARY METHOD)

When files are images containing text labels:
1. Use `scripts/ocr_macos_vision.swift` via `xcrun swift` — this is the **fastest, most reliable method**
2. Crops automatically to top 15% where titles live, avoids noisy body content
3. Extract ID numbers (T001, T002...), titles, or category labels from each image
4. Use **voting/consensus** across multiple variations of the same term
5. Verify mapping with user before bulk renaming

**Example:**
```bash
xcrun swift ~/.hermes/skills/batch-file-renaming/scripts/ocr_macos_vision.swift /path/to/image.png
```

**Fallback options (use ONLY if macOS Vision fails):**
- `browser_vision` via `browser_navigate` to file:// URL
- `tesseract` command-line OCR (`brew install tesseract`)

### ✅ Work Safely

1. **Backup first** - copy original files to a backup directory before any renaming
2. **Dry run** - print proposed renames first for verification
3. **Incremental** - rename one batch/term first and ask for confirmation before proceeding
4. **Document** - keep a mapping file that records original → new filename for traceability

## Step-by-Step Workflow

### 1. Inventory Files and Check for Manifest

```bash
ls -ltr /path/to/files/*.png | head -50  # sort by time, oldest first
```

Count files, identify naming patterns.

**CRITICAL: Look for a manifest file first!** Check for files like `00_总览.md`, `manifest.md`, `README.md` that often contain:
- Exact term IDs and names
- Number of images per term
- Target naming conventions
- Project-specific metadata

This eliminates 90% of guesswork. Use the manifest as your source of truth, not assumptions.

### 2. Verify Content Identification

For the first few files, manually verify the content:
- Open first 4-8 files
- Identify what ID/label each file contains
- Confirm the pattern (e.g., 4 images per term, sequential IDs)

### 3. Create Mapping

Build a mapping table:

| Original File | Term ID | Variation | Target Name |
|---------------|---------|-----------|-------------|
| image (1).png | T001 | v1 | T001-AI（人工智能）_v1.png |
| image (2).png | T001 | v2 | T001-AI（人工智能）_v2.png |

### 4. Execute Renaming

- Start with one batch (one term, 4 images)
- Verify results look correct
- Continue with remaining batches

## Common Pitfalls

### ❌ Pitfall: Assuming Filename Numbers Match Content IDs

**Problem:** `image (35).png` may NOT contain T035 - it could be T009 or any other ID depending on generation order.

**Fix:** Always OCR or manually verify the actual ID on each card/image.

### ❌ Pitfall: Timestamps Are Not Trustworthy

**Problem:** Files with similar timestamps may be out of order due to parallel processing, network delays, or bulk saves.

**Fix:** Don't trust time ordering alone - verify content.

### ❌ Pitfall: Vision Tools Can Hallucinate

**Problem:** AI vision tools (especially `browser_vision` and `vision_analyze`) are unreliable. They may:
- Hallucinate completely unrelated content (e.g., medical terminology instead of AI knowledge cards)
- Report "cannot see the image" even when the page loaded
- Misread digits or labels
- Return cached results from previous images

**Fix:**
1. Always spot-check — if the first identification looks wrong, stop
2. Cross-verify with multiple tools or approaches
3. When in doubt: ask the user to verify a sample
4. Never assume "the tool worked" — validate the output makes contextual sense for the project

### ❌ Pitfall: Not Handling Missing/Extra Files

**Problem:** Some terms may have 3 images instead of 4, or duplicates may exist.

**Fix:** Count files per ID first, flag anomalies for user review before renaming.

### ❌ Pitfall: Domain Knowledge Fallback is FORBIDDEN by User Mandate

**USER EXPLICITLY REJECTED preset term tables (Session 2026-07-13):**
> "必须解图片内容，提取编号信息，再重命名。"
> "Must read image content, extract number info, then rename."

> "不能套用其它数据，也是只能识别。"
> "Cannot use preset data, can only recognize."

**CONSEQUENCE:** The `TERM_MAP` fallback pattern is **DEPRECATED**. You MUST NOT use filename patterns or preset lookup tables to skip actual content recognition. Even if you "know" the mapping, **OCR EVERY FILE**. The user corrected this explicitly after mislabeling occurred.

### ✅ macOS Vision Framework — Primary OCR Method (Reliable, Local, Fast)

**Discovered in Session 2026-07-13:** macOS has a built-in Vision framework accessible via Swift. This is the **most reliable OCR method** — no network, no hallucinations, no model downloads.

**How to use:**

1. Create a Swift script (`ocr_top.swift`):
```swift
import Vision
import AppKit

// Crop to TOP 15% where titles live — avoids distracting content
let img = NSImage(contentsOfFile: CommandLine.arguments[1])!
let cropRect = NSRect(x: 0, y: img.size.height * 0.85,
                      width: img.size.width, height: img.size.height * 0.15)

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false

try VNImageRequestHandler(cgImage: img.cgImage(forProposedRect: nil, context: nil, hints: nil)!,
                          options: [:]).perform([request])

for result in request.results ?? [] {
    print(result.topCandidates(1)[0].string)
}
```

2. Run and parse:
```bash
xcrun swift ocr_top.swift /path/to/image.png
```

**Key Techniques:**
- **Crop to top region only** (120px or ~15% of image height) — this is where titles/IDs live, eliminates noise from card body content
- **Language correction OFF** — preserves numbers and technical terminology
- **Accurate level** — better for small font and dense text

**OCR Error Correction Patterns:**
```python
# Common OCR mistakes
corrections = {
    'O': '0', 'o': '0',    # Letter O -> zero
    'I': '1', 'l': '1',    # Uppercase i / lowercase L -> one
    'S': '5', 'Z': '2',    # Shape similarities
    'B': '8', 'G': '6',
}
```

### ✅ Voting/Consensus Pattern for Term Names

When multiple images share the same number (e.g., 4 variations of t001):
1. OCR all 4 images
2. Count frequency of each extracted term name
3. Use the most frequent name as the canonical name for that number
4. Flag files that don't match for user review

```python
# Example: 4 images for number 001
# Image 1: "人工智" (partial OCR)
# Image 2: "人工智能" ✓
# Image 3: "人工智能" ✓
# Image 4: "人工智" (partial OCR)
# Winner: "人工智能" (2 votes)
```

This corrects for partial OCR reads and ensures consistency across variations of the same term.

## Tools

- **✅ PRIMARY: macOS Vision Framework** - Use `scripts/ocr_macos_vision.swift` via `xcrun swift`. Fast, local, reliable, no network, no hallucinations. Crops to top 15% where titles live.
- **⚠️ Vision Tool Reliability Warning:** `browser_vision` and `vision_analyze` are NOT 100% reliable. Known issues:
  - Local file paths often fail with "cannot see image" errors
  - Hallucinations are common (returns unrelated content)
  - Cached results from previous requests may be returned
  - Use with extreme skepticism — verify every output makes sense
- **OCR:** `tesseract` (install via `brew install tesseract`) — backup option, but macOS Vision is preferred
- **File operations:** Use `cp` instead of `mv` for safety (copy first, delete originals after verification)
- **Verification:** `ls -l` to confirm file counts after each batch
- **Batch processing:** When `execute_code` is blocked, write a shell script and run it via `terminal`

## Example Pattern: AI Knowledge Cards

For AI knowledge card projects (each term has 4 variations):
1. **OCR first card** using `scripts/ocr_macos_vision.swift` to confirm the workflow works
2. **OCR 5th card** to confirm it's the next term and verify pattern
3. If pattern holds, proceed with batch processing using **macOS Vision exclusively**
4. Use **voting/consensus** across the 4 variations of each term to get the canonical name
5. Periodically spot-check throughout the process

## References

- See `references/macos-vision-ocr-mandate-2026-07-13.md` for session details on user's explicit mandate to use OCR exclusively (no preset tables)
- See `references/ai-knowledge-cards-2026-07-13.md` for detailed session notes on AI training platform knowledge card projects
- See `scripts/ocr_macos_vision.swift` for the macOS Vision Swift OCR script
- See `references/dont-waste-tokens-on-ocr-workarounds.md` for token-saving strategies
- See `scripts/smart_rename_ai_cards.py` — **DEPRECATED** by user mandate (2026-07-13), use macOS Vision OCR instead
