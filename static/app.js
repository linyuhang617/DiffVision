let currentComparisonId = null;

document.addEventListener("DOMContentLoaded", () => {
  const inputA = document.getElementById("input-a");
  const inputB = document.getElementById("input-b");
  const cardA  = document.getElementById("card-a");
  const cardB  = document.getElementById("card-b");
  const statusBar      = document.getElementById("status-bar");
  const previewSection = document.getElementById("preview-section");
  const resultSection  = document.getElementById("result-section");
  const previewA = document.getElementById("preview-a");
  const previewB = document.getElementById("preview-b");

  function showStatus(message, type) {
    statusBar.textContent = message;
    statusBar.className = `status-bar ${type}`;
    statusBar.classList.remove("hidden");
  }

  function clearStatus() {
    statusBar.className = "status-bar hidden";
    statusBar.textContent = "";
  }

  function resetResults() {
    previewSection.classList.add("hidden");
    resultSection.classList.add("hidden");
    resultSection.innerHTML = "";
    currentComparisonId = null;
  }

  inputA.addEventListener("change", () => {
    if (inputA.files.length) cardA.classList.add("has-file");
    onBothFilesReady();
  });

  inputB.addEventListener("change", () => {
    if (inputB.files.length) cardB.classList.add("has-file");
    onBothFilesReady();
  });

  function onBothFilesReady() {
    if (inputA.files.length && inputB.files.length) {
      resetResults();
      uploadFiles(inputA.files[0], inputB.files[0]);
    }
  }

  async function uploadFiles(fileA, fileB) {
    showStatus("上傳中…", "loading");
    const form = new FormData();
    form.append("file_a", fileA);
    form.append("file_b", fileB);

    let response;
    try {
      response = await fetch("/upload", { method: "POST", body: form });
    } catch {
      showStatus("網路錯誤，請確認伺服器已啟動。", "error");
      return;
    }

    let data;
    try {
      data = await response.json();
    } catch {
      showStatus("伺服器回傳格式錯誤。", "error");
      return;
    }

    if (!response.ok) {
      showStatus(data.detail ?? data.error ?? `上傳失敗（${response.status}）`, "error");
      return;
    }

    currentComparisonId = data.comparison_id;
    previewA.src = data.image_a_url;
    previewB.src = data.image_b_url;
    previewSection.classList.remove("hidden");

    clearStatus();
    runCompare();
  }

  async function runCompare() {
    showStatus("比對中…", "loading");

    let response;
    try {
      response = await fetch("/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comparison_id: currentComparisonId }),
      });
    } catch {
      showStatus("比對請求失敗。", "error");
      return;
    }

    let data;
    try {
      data = await response.json();
    } catch {
      showStatus("比對回傳格式錯誤。", "error");
      return;
    }

    if (!response.ok) {
      showStatus(data.detail ?? data.error ?? `比對失敗（${response.status}）`, "error");
      return;
    }

    clearStatus();
    showResult(data);
  }

  function showResult(data) {
    const alignTag = data.aligned
      ? `<span class="align-tag success">✓ 已自動對齊</span>`
      : `<span class="align-tag warn">⚠ 對齊失敗</span>`;

    resultSection.innerHTML = `
      <div class="similarity-card">
        <p class="similarity-label">結構相似度</p>
        <p class="similarity-score">${data.similarity}<span class="similarity-unit">%</span></p>
      </div>
      <div class="annotated-card">
        <div class="annotated-header">
          <p class="section-title">差異標記圖</p>
          ${alignTag}
        </div>
        <img src="${data.annotated_image_url}" alt="Diff result" class="annotated-img" />
      </div>
    `;
    resultSection.classList.remove("hidden");
  }
});
