import re
a = " \n asd\n asdasda\n"
# print("".join([f"<p>{i}</p>" for i in a.split("\n")]))
print(a)
print("-----")
a = re.search(r"\W+asd\W+",a)
print(a)
