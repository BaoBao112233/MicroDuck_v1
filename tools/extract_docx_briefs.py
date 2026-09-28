from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
PKG_R = "http://schemas.openxmlformats.org/package/2006/relationships"


def q(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def paragraph_text(p: ET.Element) -> str:
    chunks: list[str] = []
    for el in p.iter():
        if el.tag == q(W, "t") and el.text:
            chunks.append(el.text)
        elif el.tag == q(W, "tab"):
            chunks.append("\t")
        elif el.tag in (q(W, "br"), q(W, "cr")):
            chunks.append("\n")
    return "".join(chunks).strip()


def main() -> None:
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out / src.name)

    with zipfile.ZipFile(src) as zf:
        doc = ET.fromstring(zf.read("word/document.xml"))
        rels_root = ET.fromstring(zf.read("word/_rels/document.xml.rels"))
        rels = {
            rel.attrib["Id"]: {
                "target": rel.attrib.get("Target", ""),
                "type": rel.attrib.get("Type", ""),
                "mode": rel.attrib.get("TargetMode", ""),
            }
            for rel in rels_root.findall(q(PKG_R, "Relationship"))
        }

        events: list[dict] = []
        image_no = 0
        seen_images: dict[str, str] = {}

        for p_no, p in enumerate(doc.iter(q(W, "p")), start=1):
            text = paragraph_text(p)
            style_el = p.find(f"./{q(W, 'pPr')}/{q(W, 'pStyle')}")
            style = style_el.attrib.get(q(W, "val"), "") if style_el is not None else ""
            links = []
            for hyperlink in p.iter(q(W, "hyperlink")):
                rid = hyperlink.attrib.get(q(R, "id"))
                anchor = hyperlink.attrib.get(q(W, "anchor"))
                label = paragraph_text(hyperlink)
                target = rels.get(rid or "", {}).get("target") if rid else None
                links.append({"label": label, "target": target, "anchor": anchor})

            images = []
            for blip in p.iter(q(A, "blip")):
                rid = blip.attrib.get(q(R, "embed")) or blip.attrib.get(q(R, "link"))
                if not rid or rid not in rels:
                    continue
                target = rels[rid]["target"]
                if rid not in seen_images:
                    image_no += 1
                    source_name = Path(target).name
                    suffix = Path(source_name).suffix
                    extracted_name = f"image-{image_no:02d}{suffix}"
                    member = "word/" + target.replace("\\", "/")
                    with zf.open(member) as inp, (out / extracted_name).open("wb") as dst:
                        shutil.copyfileobj(inp, dst)
                    seen_images[rid] = extracted_name
                images.append({"rid": rid, "source": target, "file": seen_images[rid]})

            if text or links or images:
                events.append({
                    "paragraph": p_no,
                    "style": style,
                    "text": text,
                    "links": links,
                    "images": images,
                })

        result = {
            "source": str(src),
            "events": events,
            "unique_images": list(dict.fromkeys(seen_images.values())),
        }
        (out / "document-events.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(json.dumps({"output": str(out), "events": len(events), "images": image_no}, ensure_ascii=False))


if __name__ == "__main__":
    main()
