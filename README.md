# SmallCloud 
[[繁體中文]](README.zh-tw.md) [[简体中文]](README.zh-cn.md) [[英文]](README.md)  

SmallCloud is a module synchronization system built with a Flask server and a Tkinter client. It supports:

- HWID authentication between the client and server
- whitelist management and pending HWID approval
- file synchronization through the `uploads/` directory
- automatic generation of `.env`, `whitelist.txt`, and `uploads/` on first run
- client UI in Simplified Chinese, Traditional Chinese, and English
- running from source or packaged executables

## Project Structure

- `Client/`
  - `main.py`: client entry point
  - `modules/`: client logic modules
  - `lang/`: client language JSON files
- `Server/`
  - `main.py`: server entry point
  - `modules/`: server logic modules
- `packing/`: packaging scripts and configuration
- `requirements.txt`: Python dependencies
- `example.env`: sample environment config
- `whitelist-example.txt`: sample whitelist file

## Dependencies

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Run from source

Server:

```bash
cd Server
python main.py
```

Client:

```bash
cd Client
python main.py
```

### Run packaged executables

Server: run `SmallCloud Server.exe`

Client: run `SmallCloud Client.exe`

## Server Usage

1. Start the server.
2. On first run, it will create `.env`, `whitelist.txt`, and `uploads/` in the executable directory.
3. Edit `.env` and set `SERVER_SECRET_TOKEN`
4. Add authorized client HWIDs to `whitelist.txt`
5. Place files to synchronize into `uploads/`
6. Restart the server.

## Client Usage

1. Start the client.
2. Enter the server URL, e.g. `http://127.0.0.1:5000`
3. Select a local module sync directory.
4. Select a game preset (optional).
5. Click `Start Syncing`.

### Client Notes

- `server_url`: the server address, for example `http://127.0.0.1:5000`
- `mod_dir`: local sync directory where files from the server will be downloaded
- `Game Preset`: presets for common game paths
- `Switch Language`: switch between Simplified Chinese, Traditional Chinese, and English UI

## Language Support

The client currently supports:

- Simplified Chinese
- Traditional Chinese
- English

## Local Development

- Client dependencies: `tkinter`, `requests`
- Server dependencies: `Flask`, `waitress`, `python-dotenv`

## Notes

- The server and client can be deployed on the same LAN.
- For public access, use a tunneling service such as Cloudflare Tunnel.
- `.env`, `whitelist.txt`, and `uploads/` should be located in the same directory as the executable.
