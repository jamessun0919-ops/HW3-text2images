# AI 文字生成圖片 (AI Text to Image Generation)

這是一個基於 Hugging Face Serverless Inference API (採用最新 **FLUX.1-schnell** 模型) 開發的文字生成圖片 Web 應用程式。

## ⚡ Live Demo
本專案已部署至 Streamlit Cloud，您可以點擊下方連結直接線上體驗：
👉 **[Streamlit Live Demo](https://hw3-text2images02.streamlit.app/)**

---

## ✨ 主要特色 (Features)

1. **全新推論模型**：採用最新高畫質且快速的 `black-forest-labs/FLUX.1-schnell` 模型。
2. **自動中文翻譯**：整合 MyMemory 翻譯 API。使用者輸入繁體中文描述，系統會在後台自動翻譯為英文發送給模型，確保生成圖片能精準契合提示詞。
3. **高質感風格選擇**：提供 4 種預設畫風前綴（漫畫、寫實、賽博龐克、素描），一鍵套用。
4. **極簡與高質感 UI**：採用客製化 CSS 漸層背景與卡片式響應式介面。
5. **圖片一鍵下載**：生成後可直接點擊按鈕下載 PNG 圖片至您的本機裝置。
6. **多平台支援**：提供 Streamlit 主程式與傳統 HTML + Python 後端代理伺服器兩種版本。

---

## 🛠️ 安裝與執行說明 (How to Run)

### 方案 A：Streamlit 版本 (推薦，適用於雲端部署與本地執行)

#### 1. 安裝相依套件
```bash
pip install -r requirements.txt
```

#### 2. 本地啟動
```bash
streamlit run app.py
```
啟動後，瀏覽器將自動開啟 `http://localhost:8501`。

---

### 方案 B：傳統 HTML/JS + Python 代理伺服器版本

#### 1. 啟動後端 Python 伺服器
```bash
python server.py
```

#### 2. 存取網頁
開啟瀏覽器，造訪 `http://localhost:3000` 即可使用。

---

## 📦 專案結構 (Project Directory)

- `app.py`：Streamlit Web 應用程式主要程式碼。
- `requirements.txt`：Streamlit 部署所需的套件清單。
- `server.py`：傳統的 Python HTTP 代理伺服器程式碼。
- `index.html`：傳統的前端網頁檔案。
- `.gitignore`：Git 忽略清單。
