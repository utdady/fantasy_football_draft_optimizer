from __future__ import annotations

import argparse
import os
import socket
import sys

import uvicorn

from draftopt.config import ROOT


def _in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((host, port)) == 0


def main() -> None:
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    parser = argparse.ArgumentParser(description="Run the V0 draft UI")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    port = args.port
    if _in_use(args.host, port):
        raise SystemExit(
            f"Port {port} is already in use. Try: python -m draftopt.serve --port {port + 1}"
        )
    print(f"Draft UI: http://{args.host}:{port}")
    uvicorn.run("app.main:app", host=args.host, port=port, reload=False)


if __name__ == "__main__":
    main()
