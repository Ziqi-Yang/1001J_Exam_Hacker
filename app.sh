#!/usr/bin/env bash
# 设置为1是为了
gunicorn3 --thread 8  -k gevent -b 0.0.0.0:9000 app:app
