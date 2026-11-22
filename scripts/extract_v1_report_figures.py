#!/usr/bin/env python3
"""Export cropped figures from the original 2025 ALPRO report as web assets."""
from __future__ import annotations
import argparse
import hashlib
import io
from pathlib import Path
import fitz
from PIL import Image

# Original report page number (1-indexed) and crop rectangle in PDF points.
FIGURES = {
  'module-overview': (9, (68, 68, 527, 305)),
  'uml-classes': (10, (90, 108, 506, 647)),
  'er-player-round': (11, (68, 108, 528, 407)),
  'sequence-round': (12, (68, 108, 528, 670)),
  'menu': (16, (112, 145, 482, 400)),
  'bet-dashboard': (16, (112, 482, 482, 735)),
  'observation': (17, (112, 108, 482, 340)),
  'shuffle': (17, (112, 400, 482, 638)),
  'selection': (18, (112, 108, 482, 346)),
  'result': (18, (112, 405, 482, 647)),
  'functional-tests': (20, (68, 145, 528, 400)),
  'nonfunctional-tests': (20, (68, 459, 528, 655)),
}

def main():
  p=argparse.ArgumentParser()
  p.add_argument('--input',required=True,type=Path)
  p.add_argument('--out',default=Path('versions/v1/docs/figures'),type=Path)
  args=p.parse_args()
  report=fitz.open(args.input)
  text=' '.join(report[i].get_text() for i in range(min(3,len(report))))
  print(f'Report pages {len(report)}, title: {text[:170]!r}',flush=True)
  if len(report)!=22 or 'alpro' not in text.lower():
    raise RuntimeError('Expected the authentic 22-page ALPRO report')
  args.out.mkdir(parents=True,exist_ok=True)
  hashes={}
  for name,(page_no,box) in FIGURES.items():
    page=report[page_no-1]
    clip=fitz.Rect(box)&page.rect
    pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),clip=clip,alpha=False)
    img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    data=io.BytesIO()
    img.save(data,'WEBP',quality=85,method=6)
    content=data.getvalue()
    digest=hashlib.sha256(content).hexdigest()
    if digest in hashes: raise RuntimeError(f'Duplicate rendered figures {name} & {hashes[digest]}')
    hashes[digest]=name
    destination=args.out/f'alpro-v1-{name}.webp'
    destination.write_bytes(content)
    print(f'Figure {name}: p{page_no}, {img.size}, {len(content):,}B, {digest[:12]}',flush=True)

if __name__=='__main__':main()
