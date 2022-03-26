#!/usr/bin/env python3
import pickle
import re
import json
import os

from finder import Finder
from page import Page
from questionExtractor import QuestionExtractor
from flask import Flask, request, url_for, redirect, render_template, jsonify, session

class Server(Finder):
    def __init__(self,data):
        Finder.__init__(self,data)

        self.app = Flask(__name__)
        self.app.config["JSON_AS_ASCII"] = False # 如果返回json格式数据给前端，解决中文乱码问题
        self.app.config['SECRET_KEY'] = os.urandom(5)


        self.attempts = dict()
        self.test = 1

        @self.app.route("/test")
        def test():
            return str(session.get("submitted questions","error"))

        @self.app.route("/test2")
        def test2():
            return render_template("allQuestions.html")

        @self.app.route("/test3")
        def test3():
            session["submitted questions"] = [1,2]
            return "set"

        @self.app.route("/",methods=["GET","POST"])
        def index():
            if request.method == "GET":
                return render_template("index.html")
            elif request.method == "POST":
                html = request.form["html"]
                questionExtractor = QuestionExtractor(html)
                allQ = questionExtractor.getAllQuestions()
                # return Page.allQuestions(allQ)
                return render_template("allQuestions.html",questionsCollector=Page.allQuestions(allQ))


        @self.app.route("/result",methods=["POST"])
        def resultPage():
            result = dict()
            data = request.form
            options = [data[x] for x in data if x.startswith("option")]
            subKeyWords = [data[x] for x in data if x.startswith("subKeyWord") if data[x] != ""]
            for opt in options:
                result[opt] = self.find(opt,subKeyWords,bestN=4) # 返回前4个结果，如果同分则增加

            return result



        @self.app.route("/attempt",methods=["POST"])
        def attempt():
            """
            接受参数
                hash 表示question hash
                option 表示选项
            对于某个问题提交自己的结果, 直接保存在内存中
            """


            data = request.get_json()
            if data:
                pass
            else:
                data = request.get_data()
                data = json.loads(data)


            qhash = data["qhash"]
            option = data["option"]

            hasAttempt = session.get(qhash,False)
            if hasAttempt != False:
                return "has attempted"

            if qhash in self.attempts:
                if option in self.attempts[qhash]:
                    self.attempts[qhash][option] += 1
                else:
                    self.attempts[qhash][option] = 1
            else:
                self.attempts[qhash] = {option: 1}

            session[qhash] = 1

            return "success"


        @self.app.route("/preAttempts/<string:hash>")
        def preAttempts(hash):
            """
            hash 表示question hash
            返回之前对于某个问题的答案如(key为option字符串,value为选这个答案的人数) {"option 1 china": 3, "options 2 english": 2}
            对于达到多少人之后再在前端显示结果，交给前端js负责
            """
            if hash in self.attempts:
                return jsonify(self.attempts[hash])
            return "No previous attempts"

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



    def run(self,debug=False):
        self.app.run(debug=debug) # 在flaks1.0后多线程模式自动开启


dataPath = "/home/zarkli/Documents/programme/python/1001J-exam-hacker/DATA.pkl"

def loadData():
    with open(dataPath, "rb") as f:
        return pickle.load(f)

if __name__ == '__main__':
    DATA = loadData()
    server = Server(DATA)
    # print(server.search("When You Are Old",["so"],mustIncludeSubKey=False))
    server.run(debug=True)
