# DiffVision 👁️

> 上傳兩張圖片或 PDF，自動比對差異、標示變更區域、輸出結構化報告。

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![OpenCV](https://img.shields.io/badge/OpenCV-4.9-orange)

---

## 功能

- 🖼️ 支援 JPG、PNG、WebP、PDF 上傳
- 📐 自動圖片對齊（ORB + Homography）
- 🔴 差異區域標記（紅框 bounding box）
- 📊 結構相似度分數（SSIM，0–100%）
- 📦 結構化 JSON 差異報告（含位置與嚴重程度）
- ⬇️ 下載標記圖（PNG）與 JSON 報告
- 📄 PDF 多頁選擇比對

---

## 技術架構

| 層 | 技術 |
|---|---|
| 後端框架 | FastAPI 0.111 |
| 影像處理 | OpenCV 4.9 |
| 結構相似度 | scikit-image SSIM |
| 對齊算法 | ORB + Homography |
| PDF 轉圖 | PyMuPDF（fitz） |
| 前端 | Vanilla JavaScript |

---

## 快速開始

### 環境需求

- Python 3.10+

### 安裝

```bash
git clone https://github.com/linyuhang617/DiffVision.git
cd DiffVision

pip install -r requirements.txt
```

### 環境變數

複製 `.env` 並調整設定：

```env
MAX_UPLOAD_SIZE_MB=20       # 單檔上傳上限（MB）
TEMP_DIR=temp               # 暫存目錄路徑
TEMP_RETENTION_HOURS=1      # 暫存檔保留時間（小時）
```

### 啟動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

打開瀏覽器：`http://localhost:8000`

---

## API

### `POST /upload`

上傳兩張圖片或 PDF。

**Request**
```
Content-Type: multipart/form-data
file_a: <image or PDF>
file_b: <image or PDF>
```

**Response**
```json
{
  "comparison_id": "abc123...",
  "image_a_url": "/temp/abc123/a.png",
  "image_b_url": "/temp/abc123/b.png",
  "file_type_a": "image",
  "file_type_b": "pdf",
  "page_count_a": null,
  "page_count_b": 5
}
```

---

### `POST /compare`

觸發比對，回傳相似度與差異區域。

**Request**
```json
{
  "comparison_id": "abc123...",
  "page_a": 0,
  "page_b": 0
}
```

**Response**
```json
{
  "comparison_id": "abc123...",
  "similarity": 87,
  "annotated_image_url": "/temp/abc123/annotated.png",
  "aligned": true,
  "regions": [
    { "x": 10, "y": 20, "w": 100, "h": 80, "area": 8000, "severity": "high" }
  ]
}
```

嚴重程度分級：

| severity | 面積（px²） |
|---|---|
| `high` | > 5000 |
| `medium` | 500–5000 |
| `low` | 50–500 |

---

### `GET /download/{comparison_id}`

下載比對結果。

| 參數 | 說明 |
|---|---|
| `format=image` | 下載標記圖（PNG） |
| `format=json` | 下載 JSON 報告 |

---

## 專案結構

```
diffvision/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── routers/
│   │   ├── upload.py            # POST /upload
│   │   ├── compare.py           # POST /compare
│   │   └── download.py          # GET /download
│   ├── services/
│   │   ├── compare_service.py   # SSIM 計算
│   │   ├── diff_service.py      # diff map + 輪廓偵測
│   │   ├── align_service.py     # ORB 對齊
│   │   ├── region_service.py    # 區域分類
│   │   └── pdf_service.py       # PDF 轉圖
│   ├── models/
│   │   └── diff_region.py       # Pydantic schema
│   └── utils/
│       └── image_io.py          # 共用圖片讀寫
├── static/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── temp/                        # 暫存目錄（gitignore）
├── requirements.txt
└── .env
```

---

## 工作流程

1. **上傳** — 接收兩張圖片或 PDF，存入 `temp/{comparison_id}/`
2. **對齊** — ORB 特徵點匹配 + Homography 修正角度與縮放
3. **比對** — SSIM 計算結構相似度，生成 diff map
4. **標記** — 找出差異輪廓，畫紅框存 `annotated.png`
5. **報告** — 依面積分級，序列化存 `report.json`

---

## ⚠️ 已知限制

這是 v1.0，有幾個已知問題，正在規劃 v1.1 改善：

**1. 差異框不夠精確**
當兩張圖差異分布廣（例如整體構圖不同），SSIM diff map 會把大範圍都標成差異，導致紅框蓋住整張圖而非精確圈出小差異點。
適合使用的場景：同一份文件 / 截圖，只改了少數幾個地方。

**2. 對齊在某些情況下反效果**
ORB 特徵點匹配需要圖片有足夠的邊角、文字、線條特徵。若兩張圖特徵點不足（例如色塊多、線條少的插圖），homography 計算可能不準，反而讓圖片變形。目前 v1.1 規劃加入 sanity check，對齊變差時自動 fallback 用原圖。

**3. 不適合現場拍攝照片**
SSIM 的前提是兩張圖夠接近才能比對。若圖片來自不同角度、不同光線的現場拍攝，需要更強的語義對齊方案（如 DINOv2、SuperGlue），這超出目前 v1.0 的範圍。

---

## Roadmap

- [ ] v1.1 — 改善多框偵測精確度
- [ ] v1.1 — 對齊 sanity check（自動 fallback）
- [ ] v1.2 — 支援深度學習對齊方案

---

## License

MIT
