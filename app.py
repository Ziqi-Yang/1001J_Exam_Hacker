#!/usr/bin/env python3
import pickle
import json
import os

from finder import Finder
from page import Page
from questionExtractor import QuestionExtractor
from flask import Flask, request, url_for, redirect, render_template, jsonify, session

dataPath = "/home/zarkli/Documents/programme/python/1001J-exam-hacker/DATA.pkl"

def loadData():
    with open(dataPath, "rb") as f:
        return pickle.load(f)

DATA = loadData()
finder = Finder(DATA)

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False # 如果返回json格式数据给前端，解决中文乱码问题
app.config['SECRET_KEY'] = os.urandom(5)


attempts = dict()


@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        html = request.form["html"]
        questionExtractor = QuestionExtractor(html)
        allQ = questionExtractor.getAllQuestions()
        # return Page.allQuestions(allQ)
        return render_template("allQuestions.html",questionsCollector=Page.allQuestions(allQ))


@app.route("/result",methods=["POST"])
def resultPage():
    result = dict()
    searchKeys = dict()

    data = request.form
    options = [data[x] for x in data if x.startswith("option")]
    subKeyWords = [data[x] for x in data if x.startswith("subKeyWord") if data[x] != ""]
    for opt in options:
        allKeyWords = [opt,*subKeyWords]
        tmpFindings = finder.find(opt,subKeyWords,bestN=4)
        if tmpFindings != []:
            for index in range(len(tmpFindings)):
                tmpFindings[index][4] = Page.generateContent(tmpFindings[index][4],allKeyWords)
        result[opt] = tmpFindings
        searchKeys[opt] = subKeyWords
    # for opt in result:
    #     if result[opt] != []:
    #         result[opt][4] = generateContent()
    resultsContainer = Page.result(result=result,keyWords=searchKeys)

    ids = {f"block_{i+1}":options[i] for i in range(len(options))}
    result["ids"] = ids
    resultsJS = f"results = {json.dumps(result)};"
    return render_template("resultPage.html",resultsContainer=resultsContainer,resultsJS=resultsJS)



@app.route("/attempt",methods=["POST"])
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

    if qhash in attempts:
        if option in attempts[qhash]:
            attempts[qhash][option] += 1
        else:
            attempts[qhash][option] = 1
    else:
        attempts[qhash] = {option: 1}

    session[qhash] = 1

    return "success"


@app.route("/preAttempts/<string:hash>")
def preAttempts(hash):
    """
    hash 表示question hash
    返回之前对于某个问题的答案如(key为option字符串,value为选这个答案的人数) {"option 1 china": 3, "options 2 english": 2}
    对于达到多少人之后再在前端显示结果，交给前端js负责
    """
    if hash in attempts:
        return jsonify(attempts[hash])
    return "No previous attempts"




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
