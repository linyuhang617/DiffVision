import cv2
import numpy as np


def align_images(img_a: np.ndarray, img_b: np.ndarray) -> tuple[np.ndarray, bool]:
    orb = cv2.ORB_create(nfeatures=500)

    kp_a, des_a = orb.detectAndCompute(img_a, None)
    kp_b, des_b = orb.detectAndCompute(img_b, None)

    if des_a is None or des_b is None:
        return img_b, False

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(des_a, des_b)

    if len(matches) < 4:
        return img_b, False

    matches = sorted(matches, key=lambda x: x.distance)[:10]

    pts_a = np.float32([kp_a[m.queryIdx].pt for m in matches])
    pts_b = np.float32([kp_b[m.trainIdx].pt for m in matches])

    M, mask = cv2.findHomography(pts_b, pts_a, cv2.RANSAC, 5.0)

    if M is None:
        return img_b, False

    h, w = img_a.shape[:2]
    aligned = cv2.warpPerspective(img_b, M, (w, h))

    return aligned, True
