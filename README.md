# 1001J EXAM HACKER

pdf提取文本只支持行,目前不打算整合句子,毕竟是英文，断句符号与日常用途有重复，我也没研究。像`Mr.`这样的就很欠。


## Feature

- 支持多个关键字搜索
- 支持对pdf中图片ocr

## 安装依赖

### 一般运行(项目提供了现成的`DATA.pkl`)

修改`main.py`最下方的

``` python
server.search("When You Are Old",["so"],bestN=1,mustIncludeSubKey=False)
```

具体参数

``` python
"""
不区分大小写

keyWord: 必须要包含的关键字
subKeyWords: 可选择关键字,对keyWords搜索到底内容进行打分
        比如共有5个子关键字,每含有一个就加1/5分
        没子关键字表示每个都1分(满分)
mustIncludeSubKey: (如果有subKeyWords),是否至少要包含一个subKey
bestN: 最大的返回结果数量(如果同分则可能会返回多于N个),若设置为None则表示没有限制
        备注: bestN 至少为 1, 如果小于1就返回全部
"""
```


```shell
pip install -r ./requirements.txt
python main.py
```

然后浏览器会默认打开`http://127.0.0.1:5000`,请你更改地址为`http://127.0.0.1:5000/hack`



### 对于想运行完整项目(包括生成数据`DATA.pkl`)
文档待完善

1. 库依赖安装
- 对于`pymupdf`，需要安装[MuPDF](https://mupdf.com/downloads/archive)，找到最新的安装
- `pytesseract`依赖的`OCR`后端安装
见[tesseract](https://github.com/tesseract-ocr/tesseract#installing-tesseract)，若是下载了可执行文件(非安装包)，请务必将其暴露到`path`中

2. 库安装
```shell
pip install -r ./requirements.txt
```

