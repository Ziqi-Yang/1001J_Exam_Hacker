#!/usr/bin/env python3
from markupsafe import Markup
from flask import render_template
import re

class Page:
    all_questions_html = "allQuestions.html"
    result_html = "resultPage.html"

    all_questions_settings = {
        "colors": {  # 问题背景颜色交错显示
            "color1": "#f4efe1",
            "color2": "rgba(179, 179, 179,0)"
        },
    }

    singleQuestionTemplate ="""<div class="question" style="background-color: {questionColor};" id="{qhash}">
    <div class="origin">
        <div class="originTitle">
            <h2 style="color: black;">Question {questionIndex}</h2>
            <div>
                <strong style="color: grey;">Question Hash</strong>: <span style="color: rgba(136, 37, 0, 0.685);">{qhash}</span>
            </div>
            <button class="showAnswer">查看共享答案</button>
        </div>
        <div class="questionTitle">
            {questionTitle}
        </div>
        {submitAnswerDiv}
    </div>
    <div class="search">
        <form action="/result" method="post" class="search">
            <fieldset class="searchForm">
                <legend>搜索选项<small>(默认忽略大小写)</small></legend>
                <div>
                    <p style="margin: 0; padding: 0; font-size: .2em;font-style: italic;">分别作为主要关键字,根据需求修改</p>
                    {optionsForm}
                </div>
                <div>
                    {subKeyWordsForm}
                </div>
            </fieldset>
            <div class="submitButton">
                <input type="submit" value="搜索">
            </div>
        </form>
    </div>
</div>"""

    sinlgeResultTemplate = """<div class="singleResult" id="{id}">
    <div class="searchKeys">
    <span style="font-weight: bold;">主:</span><span class="key">{keyWord}</span>
    {subKeyWordsBlock}
    </div>
    <div class="information">
    <span class="file" title="{fileName}">{file}</span>
    <span class="score" title="得分">{score}</span>
    <span class="progress" title="进度">
        <span class="back" title="上一个结果"></span>
        <span class="current">{currentResultIndex}</span>/<span class="total">{totalResultsNum}</span>
        <span class="next" title="下一个结果"></span>
    </span>
    </div>
    <div class="resultArea">
        {highlightedContent}
    </div>
</div>"""

    singleResult_notFound_Template = """<div class="singleResult" id="{id}">
    <div class="searchKeys">
    <span style="font-weight: bold;">主:</span><span class="key">{keyWord}</span>
    {subKeyWordsBlock}
    </div>
    <div>未找到搜索结果</div>
</div>"""



    def __init__(self) -> None:
        pass

    @classmethod
    def allQuestions(cls,questions):
        """
        输入格式: 由 QuestionExtractor获得的所有问题的json数据

        函数只是返回 allQuestions.py所需要的questionCollector
        """
        def genOptionsForm(questionIndex:int,options:list[str]):
            res = ""
            optionIndex = 1
            for opt in options:
                res += """<label for="{questionIndex}_option_{optionIndex}">选项 {optionIndex}</label>
                <br>
                <input type="text" name="option_{optionIndex}" id="{questionIndex}_option_{optionIndex}" value="{option}">\n""".format(questionIndex=questionIndex,optionIndex=optionIndex, option = Markup.escape(opt))
                if optionIndex != len(options):
                    res += "<br>"
                optionIndex += 1
            return res

        def genSubmitAnswersDiv(qhash,options:list):
            optionList = ""
            for opt in options:
                optionList += '<option value="{option}">{option}</option>'.format(option=opt)

            res = """<div class="submitAnswer"><div>共享你的答案<br><span>(只能提交一次哦)</span></div>
                    <select>{optionList}</select>
                    <button data-qhash="{qhash}" class="submitAnswerButton">提交</button></div>""".format(optionList=optionList,qhash=qhash)

            return res

        def genSubKeyWordsForm(questionIndex):
            return """<p style="margin: 0; padding: 0; font-size: .2em;font-style: italic;">一个主要关键字结合所有次要关键字</p>
                    <label for="{questionIndex}_subKeyWord_1">次要关键字 1</label>
                    <br>
                    <input type="text" name="subKeyWord_1" id="{questionIndex}_subKeyWord_1" placeholder="没有请留空">
                    <br>
                    <label for="{questionIndex}_subKeyWord_2">次要关键字 2</label>
                    <br>
                    <input type="text" name="subKeyWord_2" id="{questionIndex}_subKeyWord_2" placeholder="key 2">
                    <br>
                    <label for="{questionIndex}_subKeyWord_3">次要关键字 3</label>
                    <br>
                    <input type="text" name="subKeyWord_3" id="{questionIndex}_subKeyWord_3" placeholder="key 3">
                    <br>
                    <label for="{questionIndex}_subKeyWord_4">次要关键字 4</label>
                    <br>
                    <input type="text" name="subKeyWord_4" id="{questionIndex}_subKeyWord_4" placeholder="key 4">""".format(questionIndex=questionIndex)


        questionsCollector = ""
        for index,question in questions.items():
            if index % 2 == 1:
                color = cls.all_questions_settings["colors"]["color1"]
            else:
                color = cls.all_questions_settings["colors"]["color2"]

            questionTitle = question["question"]
            options = question["options"]
            qhash = question["qhash"]
            submitAnswerDiv = genSubmitAnswersDiv(qhash,options)
            optionsForm = genOptionsForm(index,options)
            subKeyWordsForm = genSubKeyWordsForm(index)

            singleQuestionDiv = cls.singleQuestionTemplate.format(questionIndex = index,questionColor=color,qhash=qhash,questionTitle=questionTitle,submitAnswerDiv=submitAnswerDiv,optionsForm=optionsForm,subKeyWordsForm=subKeyWordsForm)

            questionsCollector += singleQuestionDiv + "\n"

        return questionsCollector

    @classmethod
    def generateContent(cls,raw:str,keys:list[str]):
        """
        将含有关键词的区域高亮
        这个func给server.py使用，故暴露出来了(在server.py里就处理好然后传给Page.result)
        为了防止用于高亮的html代码被替换，先使用特殊字符占位，最后再替换这些特殊字符
        """
        substitution = {
            "#$%0%$#": "<span class='highlight'>",
            "#$%1%$#": "</span>"
        }
        substitutionKeys = list(substitution.keys())

        # re.sub对于开头和结尾的字符串根据之后规则匹配不完全，故此处需要hack
        content = f"#{raw}#"
        for key in keys:
            content = re.sub(rf"(\W+)({re.escape(key)})(\W+)",rf"\g<1>{substitutionKeys[0]}\g<2>{substitutionKeys[1]}\g<3>",content,flags=re.I) # 忽略大小写
        content = content[1:-1]
        for key in substitutionKeys:
            content = content.replace(key,substitution[key])
        content = content.replace("\n","<br>")
        return content


    @classmethod
    def result(cls,result:dict,keyWords:dict):
        """
        result Page
        """
        def genSubKeyWordsBlock(subKeyWords:list[str]):
            res = '<span style="font-weight: bold;">次:</span>'
            for subKey in subKeyWords:
                res += f'<span class="key">{subKey}</span>'
            res += "\n"
            return res

        res = ""
        index = 1
        for opt in result: # 答案选项
            keyWord = opt
            subKeyWords = keyWords[opt]
            allKeys = [keyWord,*subKeyWords]
            subKeyWordsBlock  = genSubKeyWordsBlock(subKeyWords)
            searchResults = result[opt]
            if searchResults != []:
                # 只渲染第一个，之后的交给js处理
                firstRes = searchResults[0]
                score = firstRes[0]
                folderName = firstRes[1]
                fileName = firstRes[2]
                fileNameOmitted = fileName if len(fileName) < 28 else fileName[:25] + "..."
                pageNum = firstRes[3]
                file = f"{folderName}/{fileNameOmitted} - P{pageNum}"
                highlightedContent = firstRes[4] # 传入的参数已经是在server.py里highlight过的
                res += cls.sinlgeResultTemplate.format(id=f"block_{index}",keyWord=keyWord,subKeyWordsBlock=subKeyWordsBlock,fileName=fileName,file=file,score=score,currentResultIndex=1,totalResultsNum=len(searchResults),highlightedContent=highlightedContent)
            else: # 没有找到结果
                res += cls.singleResult_notFound_Template.format(id=f"block_{index}",keyWord=keyWord,subKeyWordsBlock=subKeyWordsBlock)
            index += 1

        return res


if __name__ == '__main__':
    from questionExtractor import QuestionExtractor
    with open("form-html.html") as f:
        html = f.read()
        questionExtractor = QuestionExtractor(html)
    questions = questionExtractor.getAllQuestions()
    print(Page.allQuestions(questions))
