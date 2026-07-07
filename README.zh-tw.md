# SmallCloud
[[繁體中文]](README.zh-tw.md) [[简体中文]](README.zh-cn.md) [[英文]](README.md)  

SmallCloud 是一個基於 Flask 伺服器端與 Tkinter 客戶端構建的模組同步系統。它支援：

- 客戶端與伺服器端之間的 HWID 驗證
- 白名單管理與待審 HWID 紀錄
- 通過 `uploads/` 目錄同步模組檔案
- 首次啟動會自動生成 `.env`、`whitelist.txt`、`uploads/`
- 客戶端支援簡體中文、繁體中文、英文介面
- 支援原始碼運行與打包後可執行檔運行

## 專案結構

- `Client/`
  - `main.py`：客戶端入口
  - `modules/`：客戶端邏輯模組
  - `lang/`：客戶端語言資源 JSON
- `Server/`
  - `main.py`：伺服器端入口
  - `modules/`：伺服器端邏輯模組
- `packing/`：打包腳本與設定
- `requirements.txt`：Python 依賴
- `example.env`：環境配置示例
- `whitelist-example.txt`：白名單示例

## 依賴

安裝依賴：

```bash
pip install -r requirements.txt
```

## 快速運行

### 原始碼啟動

伺服器端：

```bash
cd Server
python main.py
```

客戶端：

```bash
cd Client
python main.py
```

### 可執行檔啟動

伺服器端：執行 `SmallCloud Server.exe`

客戶端：執行 `SmallCloud Client.exe`

## 伺服器端使用

1. 啟動伺服器端。
2. 首次運行後會在可執行檔目錄生成：`.env`、`whitelist.txt`、`uploads/`
3. 編輯 `.env`，設定 `SERVER_SECRET_TOKEN`
4. 將授權的客戶端 HWID 添加到 `whitelist.txt`
5. 將要同步的檔案放入 `uploads/`
6. 重新啟動伺服器端。

## 客戶端使用

1. 啟動客戶端。
2. 填寫伺服器地址，例如 `http://127.0.0.1:5000`
3. 選擇本地模組同步目錄。
4. 選擇遊戲預設（可選）。
5. 點選“開始檢查並同步”。

### 客戶端說明

- `server_url`：伺服器地址，例如 `http://127.0.0.1:5000`
- `mod_dir`：本地模組同步目錄，伺服器端檔案將同步到該目錄
- `Game Preset`：預設遊戲路徑，可自動選擇常見模組目錄
- `Switch Language`：切換簡體中文 / 繁體中文 / 英文介面

## 多語言支援

客戶端目前支援：

- 簡體中文
- 繁體中文
- 英文

## 本地開發與調試

- 客戶端依賴：`tkinter`、`requests`
- 伺服器端依賴：`Flask`、`waitress`、`python-dotenv`

## 說明

- 伺服器端與客戶端可部署於同一區域網路內。
- 若需要公開訪問，可使用 Cloudflare Tunnel 等穿透工具。
- `.env`、`whitelist.txt`、`uploads/` 應位於可執行檔同級目錄。
