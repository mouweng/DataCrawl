# -*- codeing: utf-8 -*-
import re
import requests
from urllib import error
import os

import sys
import os
import cv2
import dlib

# 用户代理池
UAPOOL=["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chorome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.5"]

IPPOOL=[{"ipaddr":"118.187.10.11:80"},
        {"ipaddr":"60.13.42.238:9999"},
        {"ipaddr":"121.33.226.167:3128"},
        {"ipaddr":"123.56.245.138:808"},
        {"ipaddr": "114.67.237.32:808"},
        {"ipaddr": "111.177.170.31:9999"},
        {"ipaddr": "119.101.113.153:9999"},
        {"ipaddr": "116.209.54.10:9999"},
        {"ipaddr": "121.232.148.131:9000"},
        {"ipaddr": "121.232.194.238:9000"},
        {"ipaddr":"116.209.53.196:9999"}]


def getFace(word):
    input_dir = './photos_Baidu/' + word
    output_dir = './faces/' +word

    size = 64

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #使用dlib自带的frontal_face_detector作为我们的特征提取器
    detector = dlib.get_frontal_face_detector()

    index = 1
    for (path, dirnames, filenames) in os.walk(input_dir):
        for filename in filenames:
            if filename.endswith('.jpg'):
                print('processed %s --- index : %s ' % (filename, index))
                img_path = path+'/'+filename
                # 从文件读取图片
                img = cv2.imread(img_path)

                # 转为灰度图片
                # 这边设置为
                try:
                    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                except BaseException:
                    print("Error: jpg无效")
                    continue

                # 使用detector进行人脸检测 dets为返回的结果
                dets = detector(gray_img, 1)
                # 考虑到我们图片数目足量，删除人脸个数不为1的图片，因为人两个数大于1的图片往往有其他人脸存在
                if(len(dets)!=1):
                    continue

                #使用enumerate 函数遍历序列中的元素以及它们的下标
                #下标i即为人脸序号
                #left：人脸左边距离图片左边界的距离 ；right：人脸右边距离图片左边界的距离
                #top：人脸上边距离图片上边界的距离 ；bottom：人脸下边距离图片上边界的距离
                for i, d in enumerate(dets):
                    x1 = d.top() if d.top() > 0 else 0
                    y1 = d.bottom() if d.bottom() > 0 else 0
                    x2 = d.left() if d.left() > 0 else 0
                    y2 = d.right() if d.right() > 0 else 0
                    # img[y:y+h,x:x+w]
                    face = img[x1:y1,x2:y2]
                    # 调整图片的尺寸
                    face = cv2.resize(face, (size,size))
                    cv2.imshow('image',face)
                    # 保存图片
                    cv2.imwrite(output_dir+'/'+str(index)+'.jpg', face)
                    index += 1

                key = cv2.waitKey(30) & 0xff
                if key == 27:
                    sys.exit(0)



num = 0
numPicture = 0
file = './photos_Baidu/'
List = []


def Find(url):
    global List
    List = []
    print('正在检测图片总数，请稍等.....')
    t = 0
    i = 1
    s = 0
    while t < 1000:
        Url = url + str(t)
        try:
            Result = requests.get(Url, timeout=7)
        except BaseException:
            t = t + 60
            continue
        else:
            result = Result.text
            pic_url = re.findall('"objURL":"(.*?)",', result, re.S)  # 先利用正则表达式找到图片url
            s += len(pic_url)
            if len(pic_url) == 0:
                break
            else:
                List.append(pic_url)
                t = t + 60
    return s



def dowmloadPicture(html, keyword):
    global num
    # t =0
    pic_url = re.findall('"objURL":"(.*?)",', html, re.S)  # 先利用正则表达式找到图片url
    for each in pic_url:
        print('正在下载 ' + keyword + ' 第 ' + str(num + 1) + ' 张图片' + "  图片地址 ： " + str(each))
        try:
            if each is not None:
                pic = requests.get(each, timeout=7)
            else:
                continue
        except BaseException:
            print('错误，当前图片无法下载')
            continue
        else:
            string = file + r'/' + keyword + r'/' + keyword + '_' + str(num+1) + '.jpg'
            fp = open(string, 'wb')
            fp.write(pic.content)
            fp.close()
            num += 1
        if num >= numPicture:
            return



def downLoadWithName(word):
    filename = file + word
    y = os.path.exists(filename)
    if y == 1:
        print(word + '已存在,不重复下载...')
        return
    else:
        os.mkdir(filename)

    url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + word + '&pn='
    tot = Find(url)
    print('经过检测 %s 的图片共有%d张' % (word, tot))

    # 设置要爬取的图片的数量
    numPicture = 1

    t = 1
    tmp = url
    while t <= numPicture:
        try:
            url = tmp + str(t)
            result = requests.get(url, timeout=10)
        except error.HTTPError as e:
            print('网络错误，请调整网络后重试')
            t = t + 1
        else:
            dowmloadPicture(result.text, word)
            t = t + 1
    print(word + ' 搜索结束，图片下载完成')


def downLoadWithNameList(nameList):
    for name in nameList:
        print("\n=================================================================================\n")
        global num
        num = 0
        downLoadWithName(name)
        getFace(name)

if __name__ == '__main__':  # 主函数入口
    namelist = ["雷军", "李彦宏", "刘强东", "柳传志", "马化腾", "任正非", "史玉柱", "王健林", "李开复", "刘欢", "周杰伦", "薛之谦", "华晨宇", "王力宏", "王菲", "那英", "李玉刚"]
    downLoadWithNameList(namelist)


# "欧阳娜娜", "张晋", "易洋千玺", "王宝强", "刘德华", "赵丽颖", "彭于晏", "李易峰", "胡歌", "陈小春", "张雪迎"
# "王凯", "唐嫣", "吴亦凡", "王俊凯", "罗晋", "徐峥", "邓伦", "吴京", "张国立", "陈道明"
# "雷军", "李彦宏", "刘强东", "柳传志", "马化腾", "任正非", "史玉柱", "王健林", "李开复", "刘欢", "周杰伦", "薛之谦", "华晨宇", "王力宏", "王菲", "那英", "李玉刚"
