from __future__ import annotations

import html
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


DOCX = Path(r"I:\Drive\LUBYLAB SEO\LUBYLAB WATERFUL TONE-UP ESSENCE UV BLUE SHIELD CREAM-0dc9f708-cb0c-4234-a965-42220abef360.docx")
OUTPUT = Path(r"G:\Projects\PuppyPi\wordpress-assets\kem-chong-nang\article.html")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

H2 = {
    "Làn da hiện đại không chỉ đối mặt với tia UV",
    "Tổn thương đến từ sự cộng hưởng, không phải từng yếu tố riêng lẻ",
    "Các loại bức xạ này tác động lên da như thế nào?",
    "Bảo vệ da đa tầng: Tiêu chuẩn mới trong chống nắng hằng ngày",
    "Lubylab Elixir Waterfull Tone-Up Essence Sunblock - Tiêu chuẩn mới của bảo vệ da đa tầng",
    "Thành phần và công nghệ cốt lõi:",
    "BẮT ĐẦU BẢO VỆ DA ĐA TẦNG NGAY HÔM NAY CÙNG",
    "Nguồn tài liệu tham khảo:",
}
H3 = {
    "Tầng 1: Bảo vệ da dưới ánh nắng mặt trời",
    "Tầng 2: Bảo vệ da trước ánh sáng từ màn hình",
    "Tầng 3: Trung hòa tổn thương còn sót lại",
    "OPSIN-ACTIVE™:",
    "Stella-nergy™:",
    "NAD+ và NMN:",
    "Sản phẩm phù hợp với bạn nếu:",
    "Lưu ý về an toàn khi sử dụng:",
}

FIGURES = {
    "__cover__": (
        "https://lubylab.vn/wp-content/uploads/Picture1.png",
        "Kem chống nắng có thực sự bảo vệ da trước các tác nhân hằng ngày",
        "Kem chống nắng cần bảo vệ da trước nhiều tác nhân hơn tia UV.",
        900,
    ),
    "Các loại bức xạ này tác động lên da như thế nào?": (
        "https://lubylab.vn/wp-content/uploads/image-02.jpg",
        "Mức độ xuyên sâu của tia UV, ánh sáng nhìn thấy và tia hồng ngoại vào da",
        "Tia UV, ánh sáng nhìn thấy và tia hồng ngoại tác động ở những độ sâu khác nhau của da.",
        810,
    ),
    "Bảo vệ da đa tầng: Tiêu chuẩn mới trong chống nắng hằng ngày": (
        "https://lubylab.vn/wp-content/uploads/image-03.jpg",
        "Phổ ánh sáng và tác động của UVB UVA cùng ánh sáng xanh HEV lên da",
        "Mỗi vùng bức xạ tác động lên da theo cơ chế và độ sâu khác nhau.",
        900,
    ),
    "Lubylab Elixir Waterfull Tone-Up Essence Sunblock - Tiêu chuẩn mới của bảo vệ da đa tầng": (
        "https://lubylab.vn/wp-content/uploads/image-04.png",
        "Kem chống nắng Lubylab Elixir Waterfull Tone-Up Essence Sunblock",
        "Lubylab Elixir Waterfull Tone-Up Essence Sunblock SPF50+ PA++++.",
        760,
    ),
    "BẮT ĐẦU BẢO VỆ DA ĐA TẦNG NGAY HÔM NAY CÙNG": (
        "https://lubylab.vn/wp-content/uploads/lubylab-waterfull-tone-up-product-texture.jpg",
        "Lubylab Waterfull Tone-Up Essence Sunblock Cream và kết cấu sản phẩm",
        "Kết cấu mỏng nhẹ của Lubylab Waterfull Tone-Up Essence Sunblock Cream.",
        760,
    ),
}


def figure(src: str, alt: str, caption: str, width: int) -> str:
    return (
        f'<figure style="max-width:{width}px;margin:28px auto;text-align:center">'
        f'<img src="{src}" alt="{html.escape(alt)}" loading="lazy" '
        'style="display:block;width:100%;height:auto;margin:0 auto;border-radius:10px">'
        f'<figcaption style="margin-top:10px;color:#666;font-size:14px;line-height:1.5">{html.escape(caption)}</figcaption>'
        '</figure>'
    )


def read_paragraphs() -> list[str]:
    with zipfile.ZipFile(DOCX) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    lines = []
    for p in root.findall(f".//{W}body/{W}p"):
        text = "".join((t.text or "") for t in p.findall(f".//{W}t")).strip()
        if text:
            lines.append(text)
    return lines


def main() -> None:
    lines = read_paragraphs()
    if lines and lines[0].startswith("Kem chống nắng có thực sự"):
        lines = lines[1:]

    out = [figure(*FIGURES["__cover__"])]
    in_list = False
    list_section = None
    for text in lines:
        if text in H2 or text in H3:
            if in_list:
                out.append("</ul>")
                in_list = False
            if text in FIGURES and text != "BẮT ĐẦU BẢO VỆ DA ĐA TẦNG NGAY HÔM NAY CÙNG":
                out.append(figure(*FIGURES[text]))
            tag = "h2" if text in H2 else "h3"
            style = ' style="text-align:center"' if text.startswith("BẮT ĐẦU") else ""
            out.append(f"<{tag}{style}>{html.escape(text)}</{tag}>")
            list_section = text if text in {"Sản phẩm phù hợp với bạn nếu:", "Lưu ý về an toàn khi sử dụng:", "Nguồn tài liệu tham khảo:"} else None
            if text == "BẮT ĐẦU BẢO VỆ DA ĐA TẦNG NGAY HÔM NAY CÙNG":
                out.append(figure(*FIGURES[text]))
            continue

        if text == "LUBYLAB ELIXIR WATERFULL TONE-UP ESSENCE SUNBLOCK":
            out.append(f'<h2 style="text-align:center">{html.escape(text)}</h2>')
            out.append('<p style="text-align:center;margin:28px 0"><a href="https://lubylab.vn/kem-chong-nang-lubylab-elixir-waterfull-tone-up-essence-sunblock-opsin-nad-stella-nergytm-40ml/" style="display:inline-block;padding:14px 26px;background:#111;color:#fff;text-decoration:none;border-radius:6px;font-weight:700">KHÁM PHÁ SẢN PHẨM</a></p>')
            continue

        if list_section:
            if not in_list:
                out.append('<ul style="padding-left:22px">')
                in_list = True
            out.append(f"<li>{html.escape(text)}</li>")
        elif text.startswith(("Ánh sáng xanh (HEV)", "Bức xạ hồng ngoại (IR)", "Ô nhiễm môi trường")):
            if not in_list:
                out.append('<ul style="padding-left:22px">')
                in_list = True
            out.append(f"<li>{html.escape(text)}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{html.escape(text)}</p>")
    if in_list:
        out.append("</ul>")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes, {len(lines)} source paragraphs)")


if __name__ == "__main__":
    main()
