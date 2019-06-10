# -*- coding: utf-8 -*-

import jieba
import jieba.analyse
import sys, math, os, json
from os.path import isfile, join
from os import walk, listdir
import numpy as np
#繁簡轉換
from langconv import *
from sklearn import feature_extraction
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 加載 jieba 用戶字典、停用詞
jieba.load_userdict('userdict.txt')
jieba.analyse.set_stop_words('Chinese_stop.txt')

with open('2018-08-09_stories_list.json','r') as f:
    storieslist = json.load(f)
f.close()

def getarticle(q):
    weight_all,q_tfidf = getweight(w,q)
    story = getStories(weight_all, q_tfidf,sl)
    for rec in story:
        for s in storieslist['stories']:
            if rec['title'] == s['slug']:
                rec['url'] = s['url']
            else:
                continue
    return story

# 建立 stopwords 表
def buildStop():
    with open('Chinese_stop.txt', 'r', encoding = 'utf-8') as f:
        chinese_stop = []
        for word in f:
                # 換行符號只算一個字元
                chinese_stop.append(word[:-1])
        f.close()

    english_stop = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", '\n']
    
    return chinese_stop,english_stop

# load stories
def loadstories():
    stories_in_folder = [f for f in listdir('stories/') if isfile(join('stories/',f))]
    chinese_stop,english_stop = buildStop()
    words_in_each_stories = []

    for story in stories_in_folder:
        with open('stories/' + story, 'r',encoding='utf-8', errors='replace') as f:
            story_temp = f.read()
        f.close()

        story_temp = Converter('zh-hant').convert(story_temp)
        story_words = jieba.cut(story_temp,cut_all = True)
        word_list = ''
        for word in story_words:
            if word in chinese_stop or word.lower() in english_stop:
                continue
            else:
                word_list += word
                word_list += " "
#             print(word_list)
        words_in_each_stories.append(word_list)
    return stories_in_folder, words_in_each_stories

def getweight(v,q):
    #corpus 的型態是鎮列包陣列
    corpus = v
    #該類會將文本中的詞語轉換為詞頻矩陣，矩陣元素a[i][j] 表示j詞在i類文本下的詞頻
    vectorizer = CountVectorizer()
    #該類會統計每個詞語的tf-idf權值
    transformer = TfidfTransformer()
    #第一個fit_transform是計算tf-idf，第二個fit_transform是將文本轉為詞頻矩陣
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    #獲取詞袋模型中的所有詞語
    word = vectorizer.get_feature_names()
    #將tf-idf矩陣抽取出來，元素a[i][j]表示j詞在i類文本中的tf-idf權重
    all_w = tfidf.toarray()

    #########
    q_words_cut = jieba.cut(q,cut_all='True')
    q_words_string = ''
    for w in q_words_cut:
        q_words_string += w
        q_words_string += ' '

    q_words = [q_words_string]
    print(q_words)

    q_w = vectorizer.transform(q_words).toarray()
    
    return all_w, q_w

    #打印每類文本的tf-idf詞語權重，第一個for遍歷所有文本，第二個for便利某一類文本下的詞語權重
    # for i in range(len(weight)):
    #     print(u"-------這裡輸出第",i,u"類文本的詞語tf-idf權重------")
    #     for j in range(len(word)):
    #         #找出特定相關性以上的詞語
    #         if weight[i][j] > 0.05 :
    #             print(word[j],weight[i][j])

# user 的搜尋語句
def userquery(q):
    vectorizer = CountVectorizer()
    q_words_cut = jieba.cut(q,cut_all='True')
    q_words_string = ''
    for word in q_words_cut:
        q_words_string += word
        q_words_string += ' '

    q_words = [q_words_string]
    print(q_words)
    
    q_tfidf = vectorizer.transform(q_words).toarray()
    return q_tfidf

def getStories(weight_all, q_tfidf, storylist):

    highests = {'a':0}
    
    for index, vector in enumerate(weight_all):    
        vs = cosine_similarity([q_tfidf[0],vector])
        sim = vs[0,1]
        min_in_highests_key = min(highests,key = highests.get)
        min_in_highests = highests[min_in_highests_key]
        # print(min_in_highests_key,min_in_highests)
        if sim > min_in_highests:
            highests[index] = sim
            if len(highests) > 3:
                highests.pop(min_in_highests_key)
        else:
            continue
    print(highests)
    result = []
    for h in highests:
        print(type(h))
        if type(h) == 'str':
            print('yes, str')
            continue
        else:
            highests[h] = np.float64(highests[h]).item()
            print(highests[h])
            tmp = { 'number': h,
                    # [:-4] :去掉 .txt 結尾
                    'title': storylist[h][:-4],
                    'score': highests[h]
                    }
            result.append(tmp)
            print(h, highests[h], storylist[h])

    return result

sl , w = loadstories()