#!/usr/bin/env python3
"""Extract genuine V1 ALPRO report figures into individually captioned web images.

Source: the academic CardGame report preserved in Git history (Dec 2025).
Use --input to provide an original copy of the 22-page PDF.
"""
from __future__ import annotations

import argparse
import io
from pathlib import Path

import fitz
from PIL import Image, ImageOps

# 1-indexed report page, index among images placed on the page.
FIGURES = {
    "uml-classes": (10, 0, "Original UML class architecture"),
    "er-player-round": (11, 0, "Original player/round ER model"),
    "sequence-round": (12, 0, "Original complete-round sequence diagram"),
    "menu": (16, 0, "V1 nickname and avatar selection"),
    "bet-dashboard": (16, 1, "V1 stake configuration dashboard"),
    "observation": (17, 0, "V1 red-card observation stage"),
    "shuffle": (17, 1, "V1 animated card shuffle stage"),
    "selection": (18, 0, "V1 timed card selection"),
    "result": (18, 1, "V1 game-over and statistics screen"),
    "functional-tests": (20, 0, "Functional test cases from the ALPRO report"),
    "nonfunctional-tests": (20, 1, "Non-functional test plan from the ALPRO report"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", default=Path("versions/v1/docs/figures"), type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report = fitz.open(args.input)
    if len(report) != 22 or "Rouge Gagne" not in report[0].get_text():
        raise ValueError("Expected original 22-page Rouge Gagne, Noir Perd ALPRO report")
    index = ["# Original ALPRO V1 figures", "",
             "These images are cropped from the authentic 2025 academic report,",
             "not screenshots of any later software version.", ""]
    for name, (page_number, ordinal, caption) in FIGURES.items():
        page = report[page_number - 1]
        sources = page.get_images(full=True)
        if len(sources) <= ordinal:
            raise ValueError(f"Page {page_number} missing image {ordinal}: {name}")
        image = report.extract_image(sources[ordinal][0])
        src = Image.open(io.BytesIO(image["image"])).convert("RGB")
        src = ImageOps.exif_transpose(src)
        if src.width > 1300:
            src.thumbnail((1300, 2000), Image.Resampling.LANCZOS)
        file = args.out / f"alpro-v1-{name}.webp"
        src.save(file, "WEBP", quality=86, method=6)
        index.append(f"- [{caption}]({file.name}) — original report p. {page_number}")
        print(f"{name}: PDF p.{page_number} -> {file.name} ({file.stat().st_size:,} B)")
    (args.out / "ALPRO-FIGURES.md").write_text("\n".join(index) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
