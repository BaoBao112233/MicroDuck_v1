from pathlib import Path
from PIL import Image

src = Path(r"I:\Drive\Kem chong náng\image-05.png")
out_dir = Path(r"G:\Projects\PuppyPi\wordpress-assets\kem-chong-nang")
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "lubylab-waterfull-tone-up-product-texture.jpg"

with Image.open(src) as im:
    im = im.convert("RGB")
    if im.width > 1365:
        height = round(im.height * 1365 / im.width)
        im = im.resize((1365, height), Image.Resampling.LANCZOS)
    im.save(out, "JPEG", quality=88, optimize=True, progressive=True)

print(out)
print(out.stat().st_size)
