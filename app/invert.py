from PIL import Image, ImageOps
from pathlib import Path

def invert_image(src:str, dst:str):
    psrc, pdst = Path(src), Path(dst)
    img = Image.open(psrc).convert("RGB")
    ImageOps.invert(img).save(pdst, quality=95)
