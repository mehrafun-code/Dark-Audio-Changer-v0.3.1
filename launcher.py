"""Dark Audio Changer - desktop launcher.
Server chalata hai aur app ko apni window me kholta hai (pywebview). Na mile to browser me."""
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_env():
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if v.strip():
            os.environ.setdefault(k.strip(), v.strip())


def free_port(preferred=8000):
    for port in (preferred, 0):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError("Koi free port nahi mila")


def main():
    load_env()
    import uvicorn
    from app.main import app

    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)
    url = f"http://127.0.0.1:{port}"
    print("Dark Audio Changer chal raha hai:", url)

    try:
        import webview
        webview.create_window("Dark Audio Changer", url, width=1320, height=860,
                              min_size=(900, 620), background_color="#0a0707")
        webview.start()
    except Exception as e:
        print("Window nahi khuli (", e, ") - browser me khol rahe hain. Band karne ke liye Ctrl+C dabao.")
        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    server.should_exit = True


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
