#!/bin/bash
cd "$(dirname "$0")"
echo "📖 正在启动笔记阅读器..."
python3 reader/server.py
