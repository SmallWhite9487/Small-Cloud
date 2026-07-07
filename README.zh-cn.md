# SmallCloud
[[繁體中文]](README.zh-tw.md) [[简体中文]](README.zh-cn.md) [[英文]](README.md)  

SmallCloud 是一个基于 Flask 服务端与 Tkinter 客户端构建的模组同步系统。它支持：

- 客户端与服务端之间的 HWID 鉴权
- 白名单管理与待审 HWID 记录
- 通过 `uploads/` 目录同步模组文件
- 首次启动会自动生成 `.env`、`whitelist.txt`、`uploads/`
- 客户端支持简体中文、繁体中文、英文界面
- 支持源码运行与打包后可执行文件运行

## 项目结构

- `Client/`
  - `main.py`：客户端入口
  - `modules/`：客户端逻辑模块
  - `lang/`：客户端语言资源 JSON
- `Server/`
  - `main.py`：服务端入口
  - `modules/`：服务端逻辑模块
- `packing/`：打包脚本与配置
- `requirements.txt`：Python 依赖
- `example.env`：环境配置示例
- `whitelist-example.txt`：白名单示例

## 依赖

安装依赖：

```bash
pip install -r requirements.txt
```

## 快速运行

### 源码启动

服务端：

```bash
cd Server
python main.py
```

客户端：

```bash
cd Client
python main.py
```

### 可执行文件启动

服务端：运行 `SmallCloud Server.exe`

客户端：运行 `SmallCloud Client.exe`

## 服务端使用

1. 启动服务端。
2. 首次运行后会在可执行文件目录生成：`.env`、`whitelist.txt`、`uploads/`
3. 编辑 `.env`，设置 `SERVER_SECRET_TOKEN`
4. 将授权的客户端 HWID 添加到 `whitelist.txt`
5. 将要同步的文件放入 `uploads/`
6. 重新启动服务端。

## 客户端使用

1. 启动客户端。
2. 填写服务端地址，例如 `http://127.0.0.1:5000`
3. 选择本地模组同步目录。
4. 选择游戏预设（可选）。
5. 点击“开始检查并同步”。

### 客户端说明

- `server_url`：服务端地址，例如 `http://127.0.0.1:5000`
- `mod_dir`：本地模组同步目录，服务端文件将同步到该目录
- `Game Preset`：预设游戏路径，可自动选择常见模组目录
- `Switch Language`：切换简体中文 / 繁体中文 / 英文界面

## 多语言支持

客户端当前支持：

- 简体中文
- 繁体中文
- 英文

## 本地开发与调试

- 客户端依赖：`tkinter`、`requests`
- 服务端依赖：`Flask`、`waitress`、`python-dotenv`

## 说明

- 服务端与客户端可部署在同一局域网内。
- 若需要公网访问，可使用 Cloudflare Tunnel 等穿透工具。
- `.env`、`whitelist.txt`、`uploads/` 应位于可执行文件同级目录。

