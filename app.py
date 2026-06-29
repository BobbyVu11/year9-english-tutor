"""
Year 9 English Extension Tutor
================================
Local web app — no internet or extra packages required.
Just run this file and your browser will open automatically.

Usage:
  python app.py
  (or double-click run.bat on Windows)

Press Ctrl+C in this window to quit.
"""

import http.server
import socketserver
import webbrowser
import threading
import os
import sys

PORT = 5050
HOST = "localhost"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Serve files from the app directory, suppress noisy logs."""

    def log_message(self, format, *args):
        pass  # Keep the terminal clean


def open_browser():
    webbrowser.open(f"http://{HOST}:{PORT}/index.html")


def main():
    # Always serve from the folder that contains this script
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)

    # Check index.html is present
    if not os.path.isfile("index.html"):
        print("ERROR: index.html not found next to app.py")
        print(f"  Expected: {os.path.join(app_dir, 'index.html')}")
        input("Press Enter to exit.")
        sys.exit(1)

    # Allow port re-use so rapid restarts don't hit 'address in use'
    socketserver.TCPServer.allow_reuse_address = True

    print()
    print("  ╔══════════════════════════════════╗")
    print("  ║   Year 9 English Tutor           ║")
    print("  ║   Victorian Curriculum           ║")
    print("  ╚══════════════════════════════════╝")
    print()
    print(f"  Opening at  http://{HOST}:{PORT}")
    print("  Press Ctrl+C here to quit.")
    print()

    # Open the browser after a short delay so the server is ready
    threading.Timer(1.2, open_browser).start()

    with socketserver.TCPServer((HOST, PORT), QuietHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Tutor closed. See you next time!")


if __name__ == "__main__":
    main()
