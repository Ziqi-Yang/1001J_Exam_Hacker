#!/usr/bin/env python3
from bs4 import BeautifulSoup
import hashlib

class QuestionExtractor:
    def __init__(self,html):
        soup = BeautifulSoup(html,"lxml") # 需要安装lxml库
        self._form = soup.find("form",{"id": "d2l_form"})


    def _getAllQuestionTexts(self):
        """
        return: {1: ..., 2: ...}
        """
        Questions = dict()
        index = 1
        _questions = self._form.find_all("div",{"class":"dco d2l-quiz-question-autosave-container"})
        for question in _questions:
            text = question.find("div",{"class":"drt d2l-htmlblock d2l-htmlblock-deferred"}).text
            text  = text.strip()
            Questions[index] = text
            index += 1

        return Questions


    def _getAllOptions(self):
        """
        return: {1: ["xxx","yyyy","zzz"], 2: ...}
        """
        Options = dict()
        index = 1
        tables = self._form.find_all("table",{"class": "d_t"})
        for table in tables:
            trs = table.find_all("tr")
            options = [tr.text for tr in trs]
            Options[index] = options
            index += 1
        return Options

    def getAllQuestions(self):
        """
        整合所有题目和答案,并且加上内容生成的唯一hash
        return {1: {hash: hash, question: question, options: options}....}
        """
        result = dict()

        questions = self._getAllQuestionTexts()
        options = self._getAllOptions()
        for key in questions.keys():
            question = questions[key]
            option = options[key]
            # qhash = str(hash(question))
            qhash = hashlib.md5(question.encode()).hexdigest()
            result[key] = {"qhash": qhash, "question": question, "options": option}

        return result



if __name__ == '__main__':
    with open("form-html.html") as f:
        html = f.read()
        questionExtractor = QuestionExtractor(html)

    from pprint import pprint
    pprint(questionExtractor.getAllQuestions())
