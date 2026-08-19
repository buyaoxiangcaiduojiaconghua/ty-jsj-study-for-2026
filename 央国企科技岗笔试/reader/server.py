#!/usr/bin/env python3
"""央国企科技岗笔试精讲 PDF 阅读器 HTTP 服务器
启动: python3 server.py [端口号]
默认端口: 8081
"""

import http.server
import os
import sys
import webbrowser
from pathlib import Path

# 项目根目录（reader/ 的上一级）
ROOT = Path(__file__).resolve().parent.parent

# PDF 文件路径
PDF_PATH = ROOT / "资料库" / "央国企科技岗笔试精讲.pdf"


class PDFReaderHandler(http.server.SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        # 路由分发
        if self.path == "/" or self.path == "/pdf" or self.path == "/pdf-reader.html":
            self.path = "/reader/pdf-reader.html"
            return super().do_GET()

        if self.path == "/api/pdf":
            return self._serve_pdf()

        # 其他请求交给 SimpleHTTPRequestHandler 处理
        return super().do_GET()

    def _serve_pdf(self):
        """返回 PDF 文件"""
        if not PDF_PATH.exists():
            self.send_error(404, "PDF not found")
            return
        data = PDF_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/pdf")
        self.send_header("Content-Length", len(data))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        """精简日志"""
        if "/api/" in str(args[0]):
            super().log_message(format, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081

    os.chdir(str(ROOT))

    server = http.server.HTTPServer(("127.0.0.1", port), PDFReaderHandler)
    url = f"http://localhost:{port}"
    print(f"📚 央国企科技岗笔试精讲阅读器已启动")
    print(f"   地址: {url}")
    print(f"   按 Ctrl+C 停止")
    print()

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止")
        server.shutdown()


if __name__ == "__main__":
    main()
