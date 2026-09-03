# MarkDiffusion (THU-BPM)

External research backend: [`THU-BPM/MarkDiffusion`](https://github.com/THU-BPM/MarkDiffusion)
(JMLR; Apache-2.0). A **generative watermarking** toolkit for latent diffusion
models — it *embeds* marks; it does not remove them. This tree uses it as a
controlled-experiment harness and as an optional regeneration-removal engine.

## Image-only scope

Nine image algorithms in two buckets:

| Category | Algorithms | Notes |
| --- | --- | --- |
| Pattern-based | Tree-Ring, Ring-ID, ROBIN, WIND, SFW | A fixed latent/FT pattern is injected at generation and inverted for detection |
| Key-based | Gaussian-Shading, GaussMarker, PRC, SEAL | A secret key modulates the noise/latent; detection needs the key |

Video algorithms VideoShield / VideoMark are out of scope here.

## What the remover gets

- **Same-scheme detector** for the algorithms above via `AutoWatermark.load(...).detect_watermark_in_media()`. Covers the Tree-Ring-class gap in `removal-matrix.md`. It does **not** cover StegaStamp, StableSignature, or SynthID-media.
- **`DiffusionPurification`** — a blind regeneration attack (DiffPure-style: encode → partial noise → reverse-denoise) usable as a pixel-watermark remover. Exposed as `--remove-pixel diffusion` in `clean_image.py`.
- **`NeuralCodecCompression`** — codec round-trip (compressai). Not wired here.

## Honesty constraints

1. **Detection is same-scheme and same-model only.** Inversion-based detection needs the generating model (and the key for key-based schemes). It proves “this image came from *this* model/config/params.” It cannot certify that a vendor detector will fail on an arbitrary image. Same caveat as the MarkLLM text harness.
2. **`DiffusionPurification` is blind regeneration.** It reuses the *same* pipeline, so it will not defeat a watermark that is robust to its own regeneration path, and it drifts image content (more than CtrlRegen’s controllable ControlNet regeneration). Conservative strength default (0.3). Fallback/comparison engine, never a guarantee.
3. **Heavy stack.** torch ≥ 2.4,<2.11 + diffusers + a Stable Diffusion model download (~4–10 GB). GPU strongly recommended. Some HF models are gated → `HF_TOKEN` (env only, never argv).

## License / hygiene

Apache-2.0. Installed from PyPI at a pinned version (`requirements-markdiffusion.txt`) or an editable checkout at a pinned commit (`setup_markdiffusion.sh --checkout`). Never bundled into this repo.

## Harness usage

```bash
SCRIPTS=service/scripts
MD="$HOME/markdiffusion/.venv/bin/python"

"$SCRIPTS/setup_markdiffusion.sh"                     # PyPI pin default
# or: "$SCRIPTS/setup_markdiffusion.sh" --checkout    # editable pinned clone

echo "a red fox in snow" > /tmp/prompt.txt
"$MD" "$SCRIPTS/markdiffusion_harness.py" watermark /tmp/prompt.txt \
  -o /tmp/wm.png -o2 /tmp/plain.png --scheme tr --json

"$MD" "$SCRIPTS/markdiffusion_harness.py" purify /tmp/wm.png \
  -o /tmp/wm.purified.png --purification-strength 0.3 --json

"$MD" "$SCRIPTS/markdiffusion_harness.py" detect /tmp/wm.purified.png \
  --scheme tr --detector-type l1_distance --json
```

Exit codes: 0 ok · 1 runtime error · 2 bad input · 3 backend unavailable.

## References

- Paper: https://arxiv.org/abs/2509.10569
- Docs: https://markdiffusion.readthedocs.io
- HF models: https://huggingface.co/Generative-Watermark-Toolkits
