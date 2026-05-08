import cv2
import numpy as np

from app.models.diff_region import DiffRegion


def classify_regions(contours: list) -> list[DiffRegion]:
    regions = []
    for c in contours:
        area = int(cv2.contourArea(c))
        x, y, w, h = cv2.boundingRect(c)

        if area > 5000:
            severity = "high"
        elif area > 500:
            severity = "medium"
        else:
            severity = "low"

        regions.append(DiffRegion(x=x, y=y, w=w, h=h, area=area, severity=severity))

    regions.sort(key=lambda r: r.area, reverse=True)
    return regions
