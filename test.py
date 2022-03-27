import re

def generateContent(raw:str,keys:list[str]):
    """
    为了防止用于刚亮的html代码被替换，先使用特殊字符占位，最后再替换这些特殊字符
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

raw = """Landscape During the glacial period [the Ice Age] in Ireland, the island was covered with layers of ice that could be 1km thick. As this ice began to melt, slow-moving glaciers physically carved [cut up] the landscape. The monastery of Glendalough is situated in a glacial valley in county Wicklow. The monastery itself (its churches and round tower) was founded [built] on a glacial deposit of hard earth, soil and gravel [small stones]. This earth was originally dug up and pushed before a glacier as it passed through this landscape. What is the name given to these deposits of earth highlight left behind by glaciers? \nlandscape"""

print(generateContent(raw,["landscape","highlight","what"]))
