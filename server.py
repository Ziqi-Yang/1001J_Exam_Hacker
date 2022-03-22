#!/usr/bin/env python3
import pickle
import re
from flask import Flask, request, url_for, redirect

from finder import Finder

class Server(Finder):
    def __init__(self,data):
        Finder.__init__(self,data)
        self.baseUrl = "http://127.0.0.1:5000" # 后面不能加斜杠

        self.scripts = """$(document).keydown(function(event){
        if (event.keyCode == 39 || event.keyCode == 40) {
            $(location).attr("href","%s/hack?command=forward")
        } else if (event.keyCode == 37 || event.keyCode == 38) {
            $(location).attr("href","%s/hack?command=backward")
        }});""" % (self.baseUrl, self.baseUrl)

        self.css = """html{font-family:arial,sans-serif}h1{color:#353232;font-size:3em;font-weight:700;margin-top:0;margin-bottom:0}p{margin-top:.2em;margin-bottom:0}.description{background-color:#faebd7;text-align:center}.fileInfo{width:100%;margin-bottom:2em;position:relative}.path-and-page{position:absolute;font-weight:700;left:0}.progress{position:absolute;font-weight:700;right:0}.score-pos{font-weight:700;position:absolute;left:50%;transform:translate(-50%)}.score{color:#ff4500}.content{border-width:.3em;border-style:solid;border-color:#353232;margin:1em 0 0 0;padding:.2em}.highlight{background-color:orange}"""

        self.searchTemplate = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>1001J Exam Hacker</title><script src="https://cdn.bootcdn.net/ajax/libs/jquery/3.6.0/jquery.min.js"></script><style>{css}</style></head>
<body><h1>1001J Exam Hacker</h1>
    <div class="fileInfo"><span class="path-and-page">{pathAndPage}</span><span class="progress">{progress}</span><span class="score-pos">Score: <span class="score">{score}</span></span></div><hr>
    <div class="description">按左右键来切换</div>
    <div class="content">{content}</div>
</body>
<script>{scripts}</script></html>"""

        self.curPage = ""
        self.res = None
        self.resIndex = 0
        self.keyWords = []

        self.app = Flask(__name__)

        @self.app.route("/")
        def index():
            return "Hello, World!"  # FIXME

        @self.app.route("/hack",methods=["GET"])
        def hack(): # search Page
            command = request.args.get("command")
            self.execute(command)
            return self.curPage

        @self.app.route("/search",methods=["POST"])
        def search(): # search Page
            self.search(**request.get_json())
            return redirect(url_for("hack"))

        @self.app.route("/test")
        def test(): # search Page
            return redirect(url_for("hack"))



    def search(self,keyWord:str,subKeywords=[],mustIncludeSubKey=True,bestN=None):
        self.res = self.find(keyWord,subKeywords,mustIncludeSubKey,bestN)
        keyWords = subKeywords.copy()
        keyWords.append(keyWord)
        self.keyWords = keyWords


    def execute(self,command):
        def generateContent(raw,keys):
            content = raw
            for key in keys:
                content = re.sub(rf"(\W+)({key})(\W+)","\g<1><span class='highlight'>\g<2></span>\g<3>",content,flags=re.I) # 忽略大小写
                # 上面代码对于开头和结尾的字符串不会替换，故此处需要添加情况
                if content.startswith(key):
                    content = f"<span class='highlight>{key}</span>" + content[len(key):]
                elif content.endswith(key):
                    content = content[:len(content) - len(key)] + f"<span class='highlight>{key}</span>"
            content = "".join([f"<p>{i}</p>" for i in content.split("\n")])
            return content

        # if self.res == None:
        #     raise Exception("Please execute self.search first!")

        if self.res == None:
            self.curPage = "Please execute self.search first!" #FIXME
            return
        if command == "forward":
            self.resIndex += 1
            if self.resIndex == len(self.res):
                self.curPage = "exceed!" #FIXME
                return
        elif command == "backward":
            self.resIndex -= 1
            if self.resIndex == -1:
                self.curPage = "exceed!" #FIXME
                return
        # 如果输入了不存在的命令，或者没输入命令，也执行下面代码，相当于返回当前页面

        data = self.res[self.resIndex]
        content = generateContent(data[4],self.keyWords)
        params = dict(score=data[0],pathAndPage=f"{data[1]}/{data[2]} --- page{data[3]}",progress=f"{self.resIndex + 1}/{len(self.res)}",content=content)
        self.changePage(params)



    def changePage(self,params):
        """
        params: {score: int,pathAndPage: str, progress: str, content: str}
        """
        self.curPage = self.searchTemplate.format(**params,scripts=self.scripts,css=self.css)


    def run(self,debug=False):
        self.app.run(debug=debug)


dataPath = "/home/zarkli/Documents/programme/python/1001J-exam-hacker/DATA.pkl"

def loadData():
    with open(dataPath, "rb") as f:
        return pickle.load(f)

if __name__ == '__main__':
    DATA = loadData()
    server = Server(DATA)
    server.search("When You Are Old",["so"],bestN=1,mustIncludeSubKey=False)
    server.run(debug=True)
