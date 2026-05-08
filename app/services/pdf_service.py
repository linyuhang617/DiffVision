from pathlib import Path

import cv2
import fitz
import numpy as np


def pdf_page_to_image(pdf_path: Path, page_index: int) -> np.ndarray:
    doc = fitz.open(str(pdf_path))
    page = doc[page_index]
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    doc.close()
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"PDF 頁面轉圖失敗：{pdf_path} page {page_index}")
    return img


def pdf_page_count(pdf_path: Path) -> int:
    doc = fitz.open(str(pdf_path))
    count = len(doc)
    doc.close()
    return count
