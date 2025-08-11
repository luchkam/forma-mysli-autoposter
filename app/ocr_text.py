import os
OCR_ON = os.getenv("OCR","on").lower() == "on"

def has_text(img_path:str, min_chars:int=8, min_conf:float=0.65) -> bool:
    if not OCR_ON:
        return False
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        res = ocr.ocr(img_path, cls=True) or []
        chars = []
        for line in res:
            for box, (txt, prob) in line:
                if prob >= min_conf:
                    chars.append(txt)
        return len("".join(chars)) >= min_chars
    except Exception:
        # если OCR лёг — не блокируем пайплайн
        return False
