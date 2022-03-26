#!/usr/bin/env python3
import pickle
import re



class Finder:
    """
    仅针对此项目,不做通用优化
    """
    def __init__(self,data):
        self.DATA = data


    def find(self,keyWord:str,subKeywords=[],mustIncludeSubKey=True,bestN=6):
        """
        不区分大小写

        keyWord: 必须要包含的关键字
        subKeyWords: 可选择关键字,对keyWords搜索到底内容进行打分
                比如共有5个子关键字,每含有一个就加1/5分
                没子关键字表示每个都1分(满分)
        mustIncludeSubKey: (如果有subKeyWords),是否至少要包含一个subKey
        bestN: 最大的返回结果数量(如果同分则可能会返回多于N个),若设置为None则表示没有限制
                备注: bestN 至少为 1, 如果小于1就返回全部

        return [(score,dirname,filename,page,content), (...), ...]
        """
        result = []
        score = 0
        for dn in self.DATA.keys():
            for fn in self.DATA[dn].keys():
                for p in self.DATA[dn][fn].keys():
                    # re.search对于开头和结尾的字符串根据之后规则匹配不完全，故此处需要hack
                    content = f"#{self.DATA[dn][fn][p]}#"
                    if re.search(rf"\W+{re.escape(keyWord)}\W+",content,re.I) != None:
                        for key in subKeywords:
                            key = key.lower()
                            if re.search(rf"\W+{re.escape(key)}\W+",content,re.I) != None:
                                score += 1/len(subKeywords)
                        if len(subKeywords) == 0:
                            score = 1

                        score = round(score,2)
                        result.append((score,dn,fn,p,content))
                        score = 0

                    content = content[1:-1]

        result = sorted(result,key=lambda x:x[0], reverse=True)
        if mustIncludeSubKey == True:
            result = [res for res in result if res[0] != 0 ]
        if bestN != None and bestN < len(result) and bestN >= 1:
            n = bestN + 1
            if n <= len(result) and result[bestN - 1][0] == result[n - 1][0] :
                n += 1
            n -= 1
            return result[:n]
        return result


def loadData(dataPath):
    with open(dataPath, "rb") as f:
        return pickle.load(f)


if __name__ == '__main__':
    dataPath = "/home/zarkli/Documents/programme/python/1001J-exam-hacker/DATA.pkl"
    DATA = loadData(dataPath)
    finder = Finder(DATA)

    from pprint import pprint
    pprint(finder.find("When You Are Old",["soft","ie"],bestN=4,mustIncludeSubKey=False))
