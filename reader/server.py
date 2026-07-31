#!/usr/bin/env python3
"""笔记阅读器 HTTP 服务器
启动: python3 server.py [端口号]
默认端口: 8080
"""

import http.server
import json
import os
import sys
import time
import webbrowser
from pathlib import Path

# 项目根目录（reader/ 的上一级）
ROOT = Path(__file__).resolve().parent.parent

# 模块映射：id → (标签栏显示名, 文件路径)
MODULES = [
    {"id": "01", "name": "数据结构",    "file": "笔记/专业知识/01-数据结构与算法.md"},
    {"id": "02", "name": "数据库",      "file": "笔记/专业知识/02-数据库系统.md"},
    {"id": "03", "name": "计算机网络",  "file": "笔记/专业知识/03-计算机网络.md"},
    {"id": "04", "name": "操作系统",    "file": "笔记/专业知识/04-操作系统.md"},
    {"id": "05", "name": "组成原理",    "file": "笔记/专业知识/05-计算机组成与体系结构.md"},
    {"id": "06", "name": "软件工程",    "file": "笔记/专业知识/06-软件工程.md"},
    {"id": "07", "name": "信息新技术",  "file": "笔记/专业知识/07-信息新技术.md"},
    {"id": "00", "name": "公共知识",    "file": "笔记/公共知识/00-公共与行业知识.md"},
]

# 允许访问的文件白名单（相对于 ROOT）
ALLOWED_FILES = {m["file"] for m in MODULES}
ALLOWED_FILES.add("reader/reader.html")


def get_version():
    """返回所有模块文件的最大修改时间"""
    max_mtime = 0
    for m in MODULES:
        fpath = ROOT / m["file"]
        if fpath.exists():
            mtime = fpath.stat().st_mtime
            if mtime > max_mtime:
                max_mtime = mtime
    return str(max_mtime)


class ReaderHandler(http.server.SimpleHTTPRequestHandler):
    """自定义 HTTP 请求处理器"""

    def __init__(self, *args, **kwargs):
        # 让 SimpleHTTPRequestHandler 以 ROOT 为工作目录
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        # 路由分发
        if self.path == "/" or self.path == "/reader.html":
            self.path = "/reader/reader.html"
            return super().do_GET()

        if self.path == "/api/modules":
            return self._serve_json(MODULES)

        if self.path == "/api/version":
            return self._serve_json({"version": get_version()})

        if self.path.startswith("/api/content?id="):
            module_id = self.path.split("id=")[-1]
            m = next((m for m in MODULES if m["id"] == module_id), None)
            if m is None:
                self.send_error(404, "Module not found")
                return
            fpath = ROOT / m["file"]
            if not fpath.exists():
                self.send_error(404, "File not found")
                return
            content = fpath.read_text(encoding="utf-8")
            return self._serve_json({
                "content": content,
                "name": m["name"],
                "mtime": fpath.stat().st_mtime,
            })

        # 其他请求交给 SimpleHTTPRequestHandler 处理
        return super().do_GET()

    def _serve_json(self, data):
        """返回 JSON 响应"""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """精简日志，只打印 API 请求"""
        if "/api/" in str(args[0]):
            super().log_message(format, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    # 切换到项目根目录
    os.chdir(str(ROOT))

    server = http.server.HTTPServer(("127.0.0.1", port), ReaderHandler)
    url = f"http://localhost:{port}"
    print(f"📖 笔记阅读器已启动")
    print(f"   地址: {url}")
    print(f"   按 Ctrl+C 停止")
    print()

    # 自动打开浏览器
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
