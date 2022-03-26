#!/usr/bin/env python3

import os
import pickle
import sys

#pymupdf
import fitz

# OCR
from PIL import Image
import pytesseract
import numpy as np



class PreProcessor:
    """
    res文件夹中的pdf文件预处理器
    对pdf文件中的图片采用ocr识别并放到每页文字的前面
    """
    def __init__(self,rootDir):
        self.rootDir = rootDir
        self.resDir = os.path.join(rootDir,"res")
        self.tmpDir = os.path.join(rootDir,"tmp") # 过程文件
        self.saveDataPath = os.path.join(rootDir,"DATA.pkl")

    def getAllPDFfiles(self):
        """
        return: dict{dirname: [filenames]}
        """
        files = dict()
        for dp,_,fn in os.walk(self.resDir):
            dirname = os.path.basename(dp)
            if dirname != "res":
                files[dirname] = [f for f in fn if f.endswith(".pdf")]
        return files


    def recoverpix(self,doc, item):
        """
        doc: fitz.open 返回的对pdf操作的对象
        item: fitz提取出来的image对象

        return: 包含图片信息和图片内容的字典
        """

        xref = item[0]  # xref of PDF image
        smask = item[1]  # xref of its /SMask

        # special case: /SMask or /Mask exists
        if smask > 0:
            pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
            mask = fitz.Pixmap(doc.extract_image(smask)["image"])
            pix = fitz.Pixmap(pix0, mask)
            if pix0.n > 3:
                ext = "pam"
            else:
                ext = "png"

            return {  # create dictionary expected by caller
                "ext": ext,
                "colorspace": pix.colorspace.n,
                "image": pix.tobytes(ext),
            }

        # special case: /ColorSpace definition exists
        # to be sure, we convert these cases to RGB PNG images
        if "/ColorSpace" in doc.xref_object(xref, compressed=True):
            pix = fitz.Pixmap(doc, xref)
            pix = fitz.Pixmap(fitz.csRGB, pix)
            return {  # create dictionary expected by caller
                "ext": "png",
                "colorspace": 3,
                "image": pix.tobytes("png"),
            }
        return doc.extract_image(xref)

    def ocr(self,imagePath):
        img1 = np.array(Image.open(imagePath))
        text = pytesseract.image_to_string(img1)
        return text


    def extractContent(self, pdfPath):
        """
        get content of a single pdf file
        return content
        -> dict{pageNumber: pageContent}
        """
        content = dict()
        # with pdfplumber.open(pdfPath) as pdf:
        #     pageIndex = 1
        #     for page in pdf.pages:
        #         content[pageIndex] = (page.extract_text())
        #         pageIndex += 1

        with fitz.open(pdfPath) as doc:
            pageIndex = 1
            for page in doc:
                imageText = ""
                images = page.get_images()
                for img in images:
                    # 导出图片
                    image = self.recoverpix(doc,img)
                    imageFile = os.path.join(self.tmpDir,"tmpImage.{}".format(image["ext"]))
                    with open(imageFile,"wb") as f:
                        f.write(image["image"])
                    # 对导出图片执行OCR操作
                    text = self.ocr(imageFile)
                    text = text.strip()
                    if text != "":
                        imageText += text + "\n"
                content[pageIndex] = imageText + page.get_text()
                pageIndex += 1

        return content

    def extractAll(self,saveData=True):
        """
        extract all pdf contents in the res folder
        return DATA
          dict{folderName: filename: page: content}
        """
        files = self.getAllPDFfiles()
        DATA = files
        for key in DATA.keys():
            DATA[key] = {DATA[key][i]: self.extractContent(os.path.join(
                self.resDir,key,DATA[key][i]
            )) for i in range(len(DATA[key]))}
        # return DATA["w1"]["Week 1 BDIC Lecture 1 Intro Ireland notes.pdf"]
        if saveData:
            with open(self.saveDataPath, "wb") as f:
                pickle.dump(DATA,f)
                return
        else:
            return DATA






if __name__ == '__main__':
    rootDir = sys.path[0]
    # examplePDFpath = "/home/zarkli/Documents/programme/python/1001J-exam-hacker/res/w1/Week 1 BDIC Lecture 1 Intro Ireland notes.pdf"
    examplePDFpath = "/home/zarkli/Documents/programme/python/1001J-exam-hacker/res/w1/Live Hour 1 BDIC Course Structure and MCQ instructions.pdf"
    preProcessor = PreProcessor(rootDir)
    # print(preProcessor.getAllPDFfiles())
    # print(repr(preProcessor.extractContent(examplePDFpath)))
    # print(preProcessor.extractContent(examplePDFpath)[8])
    preProcessor.extractAll()
