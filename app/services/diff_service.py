from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

from app.utils import image_io


def generate_diff(
    img_a: np.ndarray,
    gray_a: np.ndarray,
    gray_b: np.ndarray,
    out_dir: Path,
) -> dict:
    _, diff = ssim(gray_a, gray_b, full=True)
    diff = (diff * 255).astype(np.uint8)

    _, thresh = cv2.threshold(
        cv2.bitwise_not(diff), 50, 255, cv2.THRESH_BINARY
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    annotated = img_a.copy()
    valid_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 50:
            continue
        valid_contours.append(c)
        x, y, cw, ch = cv2.boundingRect(c)
        cv2.rectangle(annotated, (x, y), (x + cw, y + ch), (0, 0, 255), 2)

    image_io.save_image(annotated, out_dir / "annotated.png")

    return {"contours": valid_contours}
