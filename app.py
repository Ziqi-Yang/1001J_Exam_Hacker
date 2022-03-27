#!/usr/bin/env python3
# -- coding: utf-8 --**
import pickle
import sys
import os
# from preProcess import PreProcessor
from server import Server

rootDir = sys.path[0]
dataPath = os.path.join(rootDir,"DATA.pkl")


# def preProcess():
#     """

#     对处在res文件夹中的pdf文件预处理,结果保存到DATA.pkl中
#     注意只支持到二级目录,比如 res/w1/1.pdf
#     """
#     if not os.path.exists(dataPath):
#         preProcess = PreProcessor(rootDir)
#         preProcess.extractAll(saveData=True)

def loadData():
    with open(dataPath, "rb") as f:
        return pickle.load(f)


if __name__ == '__main__':
    # preProcess()
    DATA = loadData()
    server = Server(DATA)
    server.run(host="0.0.0.0",port=9000) # 腾讯云serverless配置
