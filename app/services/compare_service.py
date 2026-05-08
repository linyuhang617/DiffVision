import numpy as np
from skimage.metrics import structural_similarity as ssim


def compute_ssim(gray_a: np.ndarray, gray_b: np.ndarray) -> int:
    """
    計算兩張灰階圖的 SSIM，回傳 0–100 整數。
    """
    score, _ = ssim(gray_a, gray_b, full=True)
    return round(score * 100)
