import urllib.request
import streamlit as st
import pendulum as pdlm
import pandas as pd
from io import StringIO
import datetime
import pytz
from contextlib import contextmanager, redirect_stdout

import requests
import argparse
import collections
import pprint
from lunar_python import Lunar, Solar
from colorama import init
from datas import *
from common import *
from collections import OrderedDict
from bidict import bidict
from openai import OpenAI
import json
import os
from requests.exceptions import Timeout, RequestException

#八字排盘库文件
Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

temps = {"甲":3, "乙":1, "丙":6, "丁":4, "戊":5, "己":-4, "庚":-1, "辛":-3, "壬":-5, "癸":-6,"子":-6, "丑":-4, "寅":3, "卯":1, "辰":-4, 
            "巳":5, "午":6, "未":3, "申":-2, "酉":-3,"戌":4, "亥":-5}


zhi_time = {"子":'23-1', "丑":'1-3', "寅":'3-5', "卯":'5-7', "辰":'7-9', 
            "巳":'9-11', "午":'11-13', "未":'13-15', "申":'15-17', "酉":'17-19',
            "戌":'19-21', "亥":'21-23'}

zhengs = "子午卯酉"

wuhangs = {
    '金':"庚辛申酉",
    '木':"甲乙寅卯",    
    '水':"壬癸子亥",
    '火':"丙丁巳午",     
    '土':"戊己丑辰未戌",         
}

ganzhi60 = bidict({
    1:"甲子", 13:"丙子", 25:"戊子", 37:"庚子", 49:"壬子", 2:"乙丑", 14:"丁丑", 26:"己丑", 38:"辛丑", 50:"癸丑", 
    3:"丙寅", 15:"戊寅", 27:"庚寅", 39:"壬寅", 51:"甲寅", 4:"丁卯", 16:"己卯", 28:"辛卯", 40:"癸卯", 52:"乙卯", 
    5:"戊辰", 17:"庚辰", 29:"壬辰", 41:"甲辰", 53:"丙辰", 6:"己巳", 18:"辛巳", 30:"癸巳", 42:"乙巳", 54:"丁巳", 
    7:"庚午", 19:"壬午", 31:"甲午", 43:"丙午", 55:"戊午", 8:"辛未", 20:"癸未", 32:"乙未", 44:"丁未", 56:"己未", 
    9:"壬申", 21:"甲申", 33:"丙申", 45:"戊申", 57:"庚申", 10:"癸酉", 22:"乙酉", 34:"丁酉", 46:"己酉", 58:"辛酉", 
    11:"甲戌", 23:"丙戌", 35:"戊戌", 47:"庚戌", 59:"壬戌", 12:"乙亥", 24:"丁亥", 36:"己亥", 48:"辛亥", 60:"癸亥"})


zhi5 = {
    "子":OrderedDict({"癸":8}), 
    "丑":OrderedDict({"己":5, "癸":2, "辛":1,}), 
    "寅":OrderedDict({"甲":5, "丙":2, "戊":1, }),
    "卯":OrderedDict({"乙":8}),
    "辰":OrderedDict({"戊":5, "乙":2, "癸":1, }),
    "巳":OrderedDict({"丙":5, "戊":2, "庚":1,}),
    "午":OrderedDict({"丁":5, "己":3, }),
    "未":OrderedDict({"己":5, "丁":2, "乙":1,}),
    "申":OrderedDict({"庚":5, "壬":2, "戊":1, }),
    "酉":OrderedDict({"辛":8}),
    "戌":OrderedDict({"戊":5, "辛":2, "丁":1 }),
    "亥":OrderedDict({"壬":5, "甲":3, })}

zhi5_list = {
    "子":["癸"], 
    "丑":["己", "癸", "辛"], 
    "寅":["甲", "丙", "戊"],
    "卯":["乙"],
    "辰":["戊", "乙", "癸"],
    "巳":[ "丙", "戊", "庚"],
    "午":["丁", "己"],
    "未":["己", "丁", "乙"],
    "申":["庚", "壬", "戊"],
    "酉":["辛"],
    "戌":["戊", "辛", "丁" ],
    "亥":["壬", "甲",]}

ShX = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
numCn = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
Week = ["日", "一", "二", "三", "四", "五", "六"]
jqmc = ["冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑","白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
jis = {0:'冬', 1:'春', 2:'夏', 3:'秋', 4:'冬'}
ymc = ["十一", "十二", "正", "二", "三", "四", "五", "六", "七", "八", "九", "十" ]
rmc = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十", "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十", "卅一"]

ten_deities = {
    '甲':bidict({'甲':'比', "乙":'劫', "丙":'食', "丁":'伤', "戊":'才',
                  "己":'财', "庚":'杀', "辛":'官', "壬":'枭', "癸":'印', "子":'沐', 
                  "丑":'冠', "寅":'建', "卯":'帝', "辰":'衰', "巳":'病', "午":'死', 
                  "未":'墓', "申":'绝', "酉":'胎', "戌":'养', "亥":'长', '库':'未_', 
                  '本':'木', '克':'土', '被克':'金', '生我':'水', '生':'火','合':'己','冲':'庚'}),
    '乙':bidict({'甲':'劫', "乙":'比', "丙":'伤', "丁":'食', "戊":'财',
                  "己":'才', "庚":'官', "辛":'杀', "壬":'印',"癸":'枭', "子":'病', 
                  "丑":'衰', "寅":'帝', "卯":'建', "辰":'冠', "巳":'沐', "午":'长',
                  "未":'养', "申":'胎', "酉":'绝', "戌":'墓', "亥":'死', '库':'未_',
                  '本':'木', '克':'土', '被克':'金', '生我':'水', '生':'火','合':'庚','冲':'辛'}),
    '丙':bidict({'丙':'比', "丁":'劫', "戊":'食', "己":'伤', "庚":'才',
                  "辛":'财', "壬":'杀', "癸":'官', "甲":'枭', "乙":'印',"子":'胎', 
                  "丑":'养', "寅":'长', "卯":'沐', "辰":'冠', "巳":'建', "午":'帝',
                  "未":'衰', "申":'病', "酉":'死', "戌":'墓', "亥":'绝', '库':'戌_',
                  '本':'火', '克':'金', '被克':'水', '生我':'木', '生':'土','合':'辛','冲':'壬'}),
    '丁':bidict({'丙':'劫', "丁":'比', "戊":'伤', "己":'食', "庚":'财',
                  "辛":'才', "壬":'官', "癸":'杀', "甲":'印',"乙":'枭', "子":'绝', 
                  "丑":'墓', "寅":'死', "卯":'病', "辰":'衰', "巳":'帝', "午":'建',
                  "未":'冠', "申":'沐', "酉":'长', "戌":'养', "亥":'胎', '库':'戌_',
                  '本':'火', '克':'金', '被克':'水', '生我':'木', '生':'土','合':'壬','冲':'癸'}),
    '戊':bidict({'戊':'比', "己":'劫', "庚":'食', "辛":'伤', "壬":'才',
                  "癸":'财', "甲":'杀', "乙":'官', "丙":'枭', "丁":'印',"子":'胎', 
                  "丑":'养', "寅":'长', "卯":'沐', "辰":'冠', "巳":'建', "午":'帝',
                  "未":'衰', "申":'病', "酉":'死', "戌":'墓', "亥":'绝', '库':'辰_',
                  '本':'土', '克':'水', '被克':'木', '生我':'火', '生':'金','合':'癸','冲':''}),
    '己':bidict({'戊':'劫', "己":'比', "庚":'伤', "辛":'食', "壬":'财',
                  "癸":'才', "甲":'官', "乙":'杀', "丙":'印',"丁":'枭',"子":'绝', 
                  "丑":'墓', "寅":'死', "卯":'病', "辰":'衰', "巳":'帝', "午":'建',
                  "未":'冠', "申":'沐', "酉":'长', "戌":'养', "亥":'胎', '库':'辰_',
                  '本':'土', '克':'水', '被克':'木', '生我':'火', '生':'金','合':'甲','冲':''}),
    '庚':bidict({'庚':'比', "辛":'劫', "壬":'食', "癸":'伤', "甲":'才',
                  "乙":'财', "丙":'杀', "丁":'官', "戊":'枭', "己":'印',"子":'死', 
                  "丑":'墓', "寅":'绝', "卯":'胎', "辰":'养', "巳":'长', "午":'沐',
                  "未":'冠', "申":'建', "酉":'帝', "戌":'衰', "亥":'病', '库':'丑_',
                  '本':'金', '克':'木', '被克':'火', '生我':'土', '生':'水','合':'乙','冲':'甲'}), 
    '辛':bidict({'庚':'劫', "辛":'比', "壬":'伤', "癸":'食', "甲":'财',
                  "乙":'才', "丙":'官', "丁":'杀', "戊":'印', "己":'枭', "子":'长', 
                  "丑":'养', "寅":'胎', "卯":'绝', "辰":'墓', "巳":'死', "午":'病',
                  "未":'衰', "申":'帝', "酉":'建', "戌":'冠', "亥":'沐', '库':'丑_',
                  '本':'金', '克':'木', '被克':'火', '生我':'土', '生':'水','合':'丙','冲':'乙'}),
    '壬':bidict({'壬':'比', "癸":'劫', "甲":'食', "乙":'伤', "丙":'才',
                  "丁":'财', "戊":'杀', "己":'官', "庚":'枭', "辛":'印',"子":'帝', 
                  "丑":'衰', "寅":'病', "卯":'死', "辰":'墓', "巳":'绝', "午":'胎',
                  "未":'养', "申":'长', "酉":'沐', "戌":'冠', "亥":'建', '库':'辰_',
                  '本':'水', '克':'火', '被克':'土', '生我':'金', '生':'木','合':'丁','冲':'丙'}),
    '癸':bidict({'壬':'劫', "癸":'比', "甲":'伤', "乙":'食', "丙":'财',
                  "丁":'才', "戊":'官', "己":'杀', "庚":'印',"辛":'枭', "子":'建', 
                  "丑":'冠', "寅":'沐', "卯":'长', "辰":'养', "巳":'胎', "午":'绝',
                  "未":'墓', "申":'死', "酉":'病', "戌":'衰', "亥":'帝', '库':'辰_',
                  '本':'水', '克':'火', '被克':'土', '生我':'金', '生':'木','合':'戊','冲':'丁'}), 

}

siling =  {                                                
        "寅": "立春后戊土七日，丙火七日，甲木十六日 立春、雨水。",
        "卯": "惊蛰后甲木十日，乙木二十日。 惊蛰、春分。",
        "辰": "清明后乙木九日，癸水三日，戊土十八日。清明、谷雨。",   
        "巳": "立夏后戊土五日，庚金九日，丙火十六日。立夏、小满。",   
        "午": "芒种后丙火十日，己土九日，丁火十一日 芒种、夏至。 ",
        "未": "小暑后丁火九日，乙木三日，己土十八日。小暑、大署。 ",
        "申": "立秋后戊土十日，壬水三日，庚金十七日。立秋、处暑。",
        "酉": "白露后庚金十日，辛金二十日。 白露、秋分。",     
        "戌": "寒露后辛金九日，丁火三日，戊土十八日。寒露、霜降。",
        "亥": "立冬后戊土七日，甲木五日，壬水十八日。立冬、小雪。",
        "子": "大雪后壬水十日，癸水二十日。 大雪、冬至。",
        "丑": "小寒后癸水九日，辛金三日，己土十八日。小寒、大寒。",  
    }

kus = {'辰':"水土", '戌':'火土', '丑':'金', '未':'木',}

gan_hes = {
    ("甲", "己"): "中正之合 化土 尊崇重大,宽厚平直。如带煞而五行无气则多嗔好怒,性梗不可屈",
    ("乙", "庚"): '''仁义之合　化金 果敢有守, 不惑柔佞,周旋唯仁,进退唯义。''',
    ("丙", "辛"): '''威制之合　化水 ''',
    ("丁", "壬"): '''淫慝之合　化木 ''',    
    ("戊", "癸"): '''无情之合　化火''',    
}

gan_chongs = {("甲", "庚"): "相冲",   ("乙", "辛"): "相冲",
              ("丙", "壬"): "相冲", ("丁", "癸"): "相冲",}    

chongs = { 
    "甲":"庚", "庚":"甲","乙":"辛", "辛":"乙","丙":"壬", "壬":"丙", "丁":"癸",
    "癸":"丁", "子":"午", "午":"子", "丑":"未", "未":"丑", "寅":"申",  "申":"寅", 
    "卯":"酉",  "酉":"卯", "辰":"戌", "戌":"辰", "巳":"亥", "亥":"巳"
}


zhi_6hes = {
    "子丑": "土",
    "寅亥": "木",
    "卯戌": "火",
    "酉辰": "金",    
    "申巳": "水",    
    "未午": "土",        
}

zhi_3hes = {"申子辰": "水 寅","巳酉丑": "金 亥",  "寅午戌": "火 申", "亥卯未": "木 巳"}
gong_he = {"申辰": '子', "巳丑": '酉', "寅戌": '午', "亥未": '卯',
           "辰申": '子', "丑巳": '酉', "戌寅": '午', "未亥": '卯',}

zhi_half_3hes = {
    ("申", "子"): "化水  马在寅",
    ("子", "辰"): "化水  马在寅",
    ("申", "辰"): "化水  马在寅",    
    ("巳", "酉"): "化金 马在亥",  
    ("酉", "丑"): "化金 马在亥",  
    ("巳", "丑"): "化金 马在亥",      
    ("寅", "午"): "化火 马在申",    
    ("午", "戌"): "化火 马在申",   
    ("寅", "戌"): "化火 马在申",   
    ("亥", "卯"): "化木 马在巳",
    ("亥","未"): "化木 马在巳",
    ( "卯", "未"): "化木 马在巳",
}

zhi_hes = {
    "申子辰": "水",
    "巳酉丑": "金",  
    "寅午戌": "火", 
    "亥卯未": "木"
}

zhi_huis = {
    "亥子丑": "水",
    "寅卯辰": "木",  
    "巳午未": "火",       
    "申酉戌": "金",
}
gong_hui = {"亥丑": '子', "寅辰": '卯', "巳未": '午', "申戌": '酉',
           "丑亥": '子', "辰寅": '卯', "未巳": '午', "戌申": '酉',}

zhi_chongs = {
    ("子", "午"): "相冲",
    ("丑", "未"): "相冲",
    ("寅", "申"): "相冲",
    ("卯", "酉"): "相冲",
    ("辰", "戌"): "相冲",   
    ("巳", "亥"): "相冲",       
}

zhi_poes = {
    ("子", "酉"): "相破",
    ("午", "卯"): "相破",
    #("巳", "申"): "相破", 
    #("寅", "亥"): "相破",
    ("辰", "丑"): "相破",   
    ("戌", "未"): "相破",       
}

gan5 = {"甲":"木", "乙":"木", "丙":"火", "丁":"火", "戊":"土", "己":"土", 
        "庚":"金", "辛":"金", "壬":"水", "癸":"水"}

zhi_wuhangs = {"子":"水", "丑":"土", "寅":"木", "卯":"木", "辰":"土", "巳":"火", 
        "午":"火", "未":"土", "申":"金", "酉":"金", "戌":"土", "亥":"水"}

relations = {
    ("金", "金"): '=', ("金", "木"): '→', ("金", "水"): '↓', ("金", "火"): '←', ("金", "土"): '↑',
    ("木", "木"): '=', ("木", "土"): '→', ("木", "火"): '↓', ("木", "金"): '←', ("木", "水"): '↑',
    ("水", "水"): '=', ("水", "火"): '→', ("水", "木"): '↓', ("水", "土"): '←', ("水", "金"): '↑',    
    ("火", "火"): '=', ("火", "金"): '→', ("火", "土"): '↓', ("火", "水"): '←', ("火", "木"): '↑',
    ("土", "土"): '=', ("土", "水"): '→', ("土", "金"): '↓', ("土", "木"): '←', ("土", "火"): '↑',

}

guans = {
    "甲":('辛',"酉","戌","丑"), "乙":('庚',"申",'巳'), "丙":("癸",'丑','辰'), 
    "丁":('壬',"亥", '申'),"戊":('乙',"卯","戌","未"), "己":('甲',"寅", "亥"), 
    "庚":('丁',"午", "戌","未"), "辛":('丙',"寅",'巳'),
    "壬":('己',"午",'未','丑'), "癸":('戊',"寅","辰",'巳','申','戌'),}

empties = {
    ('甲', '子'): ('戌','亥'), ('乙', '丑'):('戌','亥'), 
    ('丙', '寅'): ('戌','亥'), ('丁', '卯'): ('戌','亥'), 
    ('戊', '辰'): ('戌','亥'), ('己', '巳'): ('戌','亥'),
    ('庚', '午'): ('戌','亥'), ('辛', '未'): ('戌','亥'),
    ('壬', '申'): ('戌','亥'), ('癸', '酉'): ('戌','亥'),

    ('甲', '戌'): ('申','酉'), ('乙', '亥'): ('申','酉'),
    ('丙', '子'): ('申','酉'), ('丁', '丑'): ('申','酉'),
    ('戊', '寅'): ('申','酉'), ('己', '卯'): ('申','酉'),
    ('庚', '辰'):('申','酉'), ('辛', '巳'): ('申','酉'),
    ('壬', '午'): ('申','酉'), ('癸', '未'): ('申','酉'),

    ('甲', '申'): ('午','未'), ('乙', '酉'): ('午','未'),
    ('丙', '戌'): ('午','未'), ('丁', '亥'): ('午','未'),
    ('戊', '子'): ('午','未'), ('己', '丑'): ('午','未'), 
    ('庚', '寅'): ('午','未'), ('辛', '卯'): ('午','未'),
    ('壬', '辰'): ('午','未'), ('癸', '巳'): ('午','未'),

    ('甲', '午'): ('辰','己'), ('乙', '未'): ('辰','己'),
    ('丙', '申'): ('辰','己'), ('丁', '酉'): ('辰','己'),
    ('戊', '戌'): ('辰','己'), ('己', '亥'): ('辰','己'),
    ('庚', '子'): ('辰','己'), ('辛', '丑'): ('辰','己'),
    ('壬', '寅'): ('辰','己'), ('癸', '卯'): ('辰','己'),

    ('甲', '辰'): ('寅','卯'), ('乙', '巳'): ('寅','卯'),
    ('丙', '午'): ('寅','卯'), ('丁', '未'): ('寅','卯'),
    ('戊', '申'): ('寅','卯'), ('己', '酉'): ('寅','卯'),
    ('庚', '戌'): ('寅','卯'), ('辛', '亥'): ('寅','卯'),
    ('壬', '子'): ('寅','卯'), ('癸', '丑'): ('寅','卯'), 


    ('甲', '寅'): ('子','丑'), ('乙', '卯'): ('子','丑'),     
    ('丙', '辰'): ('子','丑'), ('丁', '巳'): ('子','丑'), 
    ('戊', '午'): ('子','丑'), ('己', '未'): ('子','丑'),
    ('庚', '申'): ('子','丑'), ('辛', '酉'): ('子','丑'), 
    ('壬', '戌'): ('子','丑'), ('癸', '亥'): ('子','丑'),    
}

zhi_atts = {
    "子":{"冲":"午", "刑":"卯", "被刑":"卯", "合":("申","辰"), "会":("亥","丑"), '害':'未', '破':'酉', "六":"丑","暗":"",},
    "丑":{"冲":"未", "刑":"戌", "被刑":"未", "合":("巳","酉"), "会":("子","亥"), '害':'午', '破':'辰', "六":"子","暗":"寅",},
    "寅":{"冲":"申", "刑":"巳", "被刑":"申", "合":("午","戌"), "会":("卯","辰"), '害':'巳', '破':'亥', "六":"亥","暗":"丑",},
    "卯":{"冲":"酉", "刑":"子", "被刑":"子", "合":("未","亥"), "会":("寅","辰"), '害':'辰', '破':'午', "六":"戌","暗":"申",},
    "辰":{"冲":"戌", "刑":"辰", "被刑":"辰", "合":("子","申"), "会":("寅","卯"), '害':'卯', '破':'丑', "六":"酉","暗":"",},
    "巳":{"冲":"亥", "刑":"申", "被刑":"寅", "合":("酉","丑"), "会":("午","未"), '害':'寅', '破':'申', "六":"申","暗":"",},
    "午":{"冲":"子", "刑":"午", "被刑":"午", "合":("寅","戌"), "会":("巳","未"), '害':'丑', '破':'卯', "六":"未","暗":"亥",},
    "未":{"冲":"丑", "刑":"丑", "被刑":"戌", "合":("卯","亥"), "会":("巳","午"), '害':'子', '破':'戌', "六":"午","暗":"",},
    "申":{"冲":"寅", "刑":"寅", "被刑":"巳", "合":("子","辰"), "会":("酉","戌"), '害':'亥', '破':'巳', "六":"巳","暗":"卯",},
    "酉":{"冲":"卯", "刑":"酉", "被刑":"酉", "合":("巳","丑"), "会":("申","戌"), '害':'戌', '破':'子', "六":"辰","暗":"",},
    "戌":{"冲":"辰", "刑":"未", "被刑":"丑", "合":("午","寅"), "会":("申","酉"), '害':'酉', '破':'未', "六":"卯","暗":"",},
    "亥":{"冲":"巳", "刑":"亥", "被刑":"亥", "合":("卯","未"), "会":("子","丑"), '害':'申', '破':'寅', "六":"寅","暗":"午",},
}

nayins = {
    ('甲', '子'): '海中金', ('乙', '丑'): '海中金', ('壬', '寅'): '金泊金', ('癸', '卯'): '金泊金',
    ('庚', '辰'): '白蜡金', ('辛', '巳'): '白蜡金', ('甲', '午'): '砂中金', ('乙', '未'): '砂中金',
    ('壬', '申'): '剑锋金', ('癸', '酉'): '剑锋金', ('庚', '戌'): '钗钏金', ('辛', '亥'): '钗钏金',
    ('戊', '子'): '霹雳火', ('己', '丑'): '霹雳火', ('丙', '寅'): '炉中火', ('丁', '卯'): '炉中火',
    ('甲', '辰'): '覆灯火', ('乙', '巳'): '覆灯火', ('戊', '午'): '天上火', ('己', '未'): '天上火',
    ('丙', '申'): '山下火', ('丁', '酉'): '山下火', ('甲', '戌'): '山头火', ('乙', '亥'): '山头火',
    ('壬', '子'): '桑柘木', ('癸', '丑'): '桑柘木', ('庚', '寅'): '松柏木', ('辛', '卯'): '松柏木',
    ('戊', '辰'): '大林木', ('己', '巳'): '大林木', ('壬', '午'): '杨柳木', ('癸', '未'): '杨柳木',
    ('庚', '申'): '石榴木', ('辛', '酉'): '石榴木', ('戊', '戌'): '平地木', ('己', '亥'): '平地木',
    ('庚', '子'): '壁上土', ('辛', '丑'): '壁上土', ('戊', '寅'): '城头土', ('己', '卯'): '城头土',
    ('丙', '辰'): '砂中土', ('丁', '巳'): '砂中土', ('庚', '午'): '路旁土', ('辛', '未'): '路旁土',
    ('戊', '申'): '大驿土', ('己', '酉'): '大驿土', ('丙', '戌'): '屋上土', ('丁', '亥'): '屋上土',
    ('丙', '子'): '涧下水', ('丁', '丑'): '涧下水', ('甲', '寅'): '大溪水', ('乙', '卯'): '大溪水',
    ('壬', '辰'): '长流水', ('癸', '巳'): '长流水', ('丙', '午'): '天河水', ('丁', '未'): '天河水',
    ('甲', '申'): '井泉水', ('乙', '酉'): '井泉水', ('壬', '戌'): '大海水', ('癸', '亥'): '大海水',    
}

year_shens = {
    '孤辰':{"子":"寅", "丑":"寅", "寅":"巳", "卯":"巳", "辰":"巳", "巳":"申", 
              "午":"申", "未":"申", "申":"亥", "酉":"亥", "戌":"亥", "亥":"寅"},
    '寡宿':{"子":"戌", "丑":"戌", "寅":"丑", "卯":"丑", "辰":"丑", "巳":"辰", 
              "午":"辰", "未":"辰", "申":"未", "酉":"未", "戌":"未", "亥":"戌"},   
    '大耗':{"子":"巳未", "丑":"午申", "寅":"未酉", "卯":"申戌", "辰":"酉亥", "巳":"戌子", 
              "午":"亥丑", "未":"子寅", "申":"丑卯", "酉":"寅辰", "戌":"卯巳", "亥":"辰午"},      
}

month_shens = {
    '天德':{"子":"巳", "丑":"庚", "寅":"丁", "卯":"申", "辰":"壬", "巳":"辛", 
            "午":"亥", "未":"甲", "申":"癸", "酉":"寅", "戌":"丙", "亥":"乙"},
    '月德':{"子":"壬", "丑":"庚", "寅":"丙", "卯":"甲", "辰":"壬", "巳":"庚", 
              "午":"丙", "未":"甲", "申":"壬", "酉":"庚", "戌":"丙", "亥":"甲"},
}
    

day_shens = { 
    '将星':{"子":"子", "丑":"酉", "寅":"午", "卯":"卯", "辰":"子", "巳":"酉", 
              "午":"午", "未":"卯", "申":"子", "酉":"酉", "戌":"午", "亥":"卯"},      
    '华盖':{"子":"辰", "丑":"丑", "寅":"戌", "卯":"未", "辰":"辰", "巳":"丑", 
              "午":"戌", "未":"未", "申":"辰", "酉":"丑", "戌":"戌", "亥":"未"}, 
    '驿马': {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", 
            "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"},
    '劫煞': {"子":"巳", "丑":"寅", "寅":"亥", "卯":"申", "辰":"巳", "巳":"寅", 
         "午":"亥", "未":"申", "申":"巳", "酉":"寅", "戌":"亥", "亥":"申"},
    '亡神': {"子":"亥", "丑":"申", "寅":"巳", "卯":"寅", "辰":"亥", "巳":"申", 
            "午":"巳", "未":"寅", "申":"亥", "酉":"申", "戌":"巳", "亥":"寅"},    
    '桃花': {"子":"酉", "丑":"午", "寅":"卯", "卯":"子", "辰":"酉", "巳":"午", 
            "午":"卯", "未":"子", "申":"酉", "酉":"午", "戌":"卯", "亥":"子"},        
}

g_shens = {
    '天乙':{"甲":'未丑',  "乙":"申子", "丙":"酉亥", "丁":"酉亥", "戊":'未丑', "己":"申子", 
            "庚": "未丑", "辛":"寅午", "壬": "卯巳", "癸":"卯巳"},
    '文昌':{"甲":'巳', "乙":"午", "丙":"申", "丁":"酉", "戊":"申", "己":"酉", 
            "庚": "亥", "辛":"子", "壬": "寅", "癸":"丑"},   
    '阳刃':{"甲":'卯', "乙":"", "丙":"午", "丁":"", "戊":"午", "己":"", 
            "庚": "酉", "辛":"", "壬": "子", "癸":""},     
    '红艳':{"甲":'午', "乙":"午", "丙":"寅", "丁":"未", "戊":"辰", "己":"辰", 
            "庚": "戌", "辛":"酉", "壬": "子", "癸":"申"},       
}

@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

#排盘函数和流程
def get_gen(gan, zhis):
    zhus = []
    zhongs = []
    weis = []
    result = ""
    for item in zhis:
        zhu = zhi5_list[item][0]
        if ten_deities[gan]['本'] == ten_deities[zhu]['本']:
            zhus.append(item)

    for item in zhis:
        if len(zhi5_list[item]) ==1:
            continue
        zhong = zhi5_list[item][1]
        if ten_deities[gan]['本'] == ten_deities[zhong]['本']:
            zhongs.append(item)

    for item in zhis:
        if len(zhi5_list[item]) < 3:
            continue
        zhong = zhi5_list[item][2]
        if ten_deities[gan]['本'] == ten_deities[zhong]['本']:
            weis.append(item)

    if not (zhus or zhongs or weis):
        return "无根"
    else:
        result = result + "强：{}{}".format(''.join(zhus), chr(12288)) if zhus else result
        result = result + "中：{}{}".format(''.join(zhongs), chr(12288)) if zhongs else result
        result = result + "弱：{}".format(''.join(weis)) if weis else result
        return result

def gan_zhi_he(zhu):
    gan, zhi = zhu
    if ten_deities[gan]['合'] in zhi5[zhi]:
        return "|"
    return ""

def get_gong(zhis):
    result = []
    for i in range(3):
        if  gans[i] != gans[i+1]:
            continue
        zhi1 = zhis[i]
        zhi2 = zhis[i+1]
        if abs(Zhi.index(zhi1) - Zhi.index(zhi2)) == 2:
            value = Zhi[(Zhi.index(zhi1) + Zhi.index(zhi2))//2]
            #if value in ("丑", "辰", "未", "戌"):
            result.append(value)
        if (zhi1 + zhi2 in gong_he) and (gong_he[zhi1 + zhi2] not in zhis):
            result.append(gong_he[zhi1 + zhi2]) 
            
        #if (zhi1 + zhi2 in gong_hui) and (gong_hui[zhi1 + zhi2] not in zhis):
            #result.append(gong_hui[zhi1 + zhi2])             
        
    return result


def get_shens(gans, zhis, gan_, zhi_):
    
    all_shens = []
    for item in year_shens:
        if zhi_ in year_shens[item][zhis.year]:    
            all_shens.append(item)
                
    for item in month_shens:
        if gan_ in month_shens[item][zhis.month] or zhi_ in month_shens[item][zhis.month]:     
            all_shens.append(item)
                
    for item in day_shens:
        if zhi_ in day_shens[item][zhis.day]:     
            all_shens.append(item)
                
    for item in g_shens:
        if zhi_ in g_shens[item][me]:    
            all_shens.append(item) 
    if all_shens:  
        return "  神:" + ' '.join(all_shens)
    else:
        return ""
                
def jin_jiao(first, second):
    return True if Zhi.index(second) - Zhi.index(first) == 1 else False

def is_ku(zhi):
    return True if zhi in "辰戌丑未" else False  

def zhi_ku(zhi, items):
    return True if is_ku(zhi) and min(zhi5[zhi], key=zhi5[zhi].get) in items else False

def is_yang():
    return True if Gan.index(me) % 2 == 0 else False

def not_yang():
    return False if Gan.index(me) % 2 == 0 else True

def gan_ke(gan1, gan2):
    return True if ten_deities[gan1]['克'] == ten_deities[gan2]['本'] or ten_deities[gan2]['克'] == ten_deities[gan1]['本'] else False

def check_gan(gan, gans):
    result = ''
    if ten_deities[gan]['合'] in gans:
        result += "合" + ten_deities[gan]['合']
    if ten_deities[gan]['冲'] in gans:
        result += "冲" + ten_deities[gan]['冲']
    return result

def yinyang(item):
    if item in Gan:
        return '＋' if Gan.index(item)%2 == 0 else '－'
    else:
        return '＋' if Zhi.index(item)%2 == 0 else '－'
    
def yinyangs(zhis):
    result = []
    for item in zhis:
        result.append(yinyang(item))
    if set(result) == set('＋'):
        print("四柱全阳")
    if set(result) == set('－'):
        print("四柱全阴")

def get_empty(zhu, zhi):
    empty = empties[zhu]
    if zhi in empty:
        return "空"
    return ""

def get_zhi_detail(zhi, me, multi=1):
    out = ''
    for gan in zhi5[zhi]:
        out = out + "{}{}{}{} ".format(gan, gan5[gan], zhi5[zhi][gan]*multi,  
                                       ten_deities[me][gan])
    return out

def check_gong(zhis, n1, n2, me, hes, desc='三合拱'):
    result = ''
    if zhis[n1] + zhis[n2] in hes:
        gong = hes[zhis[n1] + zhis[n2]] 
        if gong not in zhis:
            result += "\t{}：{}{}-{}[{}]".format(
                desc, zhis[n1], zhis[n2], gong, get_zhi_detail(gong, me))
    return result

#页面布局配置
st.set_page_config(layout="wide",page_title="奇門 - 八字 命理")
pan,mingli,log,links = st.tabs([' 🧮八字排盘 ', ' 📜八字命理 ', ' 📚古籍 ',' 🆕更新 ' ])
# 创建标签页
#侧边栏控件
with st.sidebar:
    # 设置日期选择器的最小和最大日期
    min_date = pd.Timestamp('1900-01-01')
    max_date = pd.Timestamp.now()
    # 创建一个日期选择器，允许用户选择从1900年到当前日期的日期
    pp_date = st.date_input("日期", pd.Timestamp.now().date(), min_value=min_date.date(), max_value=max_date.date())
    #pp_date=st.date_input("日期",pdlm.now(tz='Asia/Shanghai').date())  # 日期选择
    pp_time = st.text_input('输入时间(如: 18:30)', '')  # 时间输入
    #zuobiao = st.text_input('请输入真实事件作为参考坐标', '')  # 事件输入
    option = st.selectbox('性别', (' 男 ', ' 女 '))  # 排盘类型选择
    #option2 = st.selectbox('命理事项', (' 财运 ',' 官运 ',' 姻缘 '))  # 排盘方法选择
    num = dict(zip([' 男 ', ' 女 '],[1,2])).get(option)  # 映射选项到数值
    #pai = dict(zip([' 财运 ',' 官运 ',' 姻缘 '],[1,2,3])).get(option2)  # 映射排盘方法
    # 日期时间解析
    p = str(pp_date).split("-")
    pp = str(pp_time).split(":")
    y = int(p[0])  # 年
    m = int(p[1])  # 月
    d = int(p[2])  # 日
    # 处理时间输入
    try:
        h = int(pp[0])    # 时
        mintue = int(pp[1])  # 分
    except ValueError:
        pass
    # 按钮控件
    manual = st.button('八字排盘')  # 手动排盘
    #instant = st.button('即時')  # 即时排盘

#核心排盘逻辑
with pan:
    st.header('八字排盘')
    eg = list("巽離坤震兌艮坎乾")

    # 定义程序描述信息
    description = '''
        这是一个用于计算八字的程序。
        输入日期和时间，程序将输出对应的天干地支信息。
    '''
    # 创建命令行解析器
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    # 添加位置参数
    parser.add_argument('year', type=int, help='年份，例如 2023')
    parser.add_argument('month', type=int, help='月份，例如 10')
    parser.add_argument('day', type=int, help='日期，例如 15')
    parser.add_argument('time', help='时间，格式为 HH:MM，例如 12:00')

    # 添加可选参数
    parser.add_argument("--start", type=int, default=1850, help="起始年份，默认为 1850")
    parser.add_argument("--end", type=int, default=2030, help="结束年份，默认为 2030")
    parser.add_argument('-b', action="store_true", help="直接输入八字")
    parser.add_argument('-g', action="store_true", help="是否采用公历")
    parser.add_argument('-r', action="store_true", help="是否为闰月，仅适用于农历")
    parser.add_argument('-n', action="store_true", help="是否为女性，默认为男性")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0 Rongzhong xu 2022 06 15')

    
    
    
    output2 = st.empty()
    with st_capture(output2.code):
        if manual:
            if num == 1:
                args = [
                     p[0], p[1], p[2], pp_time,  # year, month, day, time
                     '--start', '1900',            # --start
                     '--end', '2050',              # --end
                     '-g'      # -b, -g, -r, -n
                       ]

                xingbie = ['男']
            else:
                args = [
                     p[0], p[1], p[2], pp_time,  # year, month, day, time
                     '--start', '1900',            # --start
                     '--end', '2050',              # --end
                     '-g'  , '-n'      # -b, -g, -r, -n
                       ]

                xingbie = ['女']
                


            # 解析参数
            options = parser.parse_args(args)

            # 定义 namedtuple 用于存储天干和地支信息
            Gans = collections.namedtuple("Gans", "year month day time")
            Zhis = collections.namedtuple("Zhis", "year month day time")

            # 打印分隔符
            print("-" * 120)

            # 打印输入的参数
            print(f"输入的日期和时间：{options.year}年{options.month}月{options.day}日 {options.time}")
            print(f"起始年份：{options.start}")
            print(f"结束年份：{options.end}")
            print(f"是否采用公历：{options.g}")
            print(f"是否为女性：{options.n}")

            #排盘
            if options.g:
                # 使用公历日期
                # 拆分时间字符串为小时和分钟
                time_parts = options.time.split(":")
                hour = int(time_parts[0])
                minute = int(time_parts[1])
        
                solar = Solar.fromYmdHms(y, m, 
                                         d, h, mintue, 0)
                lunar = solar.getLunar()
                #solar = Solar.fromYmdHms(int(options.year), int(options.month), int(options.day), int(options.time), 0, 0)
                #lunar = solar.getLunar()
            else:
                month_ = int(options.month)*-1 if options.r else int(options.month)
                lunar = Lunar.fromYmdHms(int(options.year), month_, int(options.day),int(options.time), 0, 0)
                solar = lunar.getSolar()

            day = lunar
            ba = lunar.getEightChar() 
            gans = Gans(year=ba.getYearGan(), month=ba.getMonthGan(), day=ba.getDayGan(), time=ba.getTimeGan())
            zhis = Zhis(year=ba.getYearZhi(), month=ba.getMonthZhi(), day=ba.getDayZhi(), time=ba.getTimeZhi())

            #计算四柱
            me = gans.day
            month = zhis.month
            alls = list(gans) + list(zhis)
            zhus = [item for item in zip(gans, zhis)]

            # 计算大运
            seq = Gan.index(gans.year)
            if options.n:
                if seq % 2 == 0:
                    direction = -1
                else:
                    direction = 1
            else:
                if seq % 2 == 0:
                    direction = 1
                else:
                    direction = -1

            dayuns = []
            gan_seq = Gan.index(gans.month)
            zhi_seq = Zhi.index(zhis.month)
            for i in range(12):
                gan_seq += direction
                zhi_seq += direction
                dayuns.append(Gan[gan_seq%10] + Zhi[zhi_seq%12])

            yun = ba.getYun(not options.n) 
            #yun.getStartSolar().toFullString().split()[0]
            print(f"八字：{zhus}")
            print(f"大运：{dayuns}")
            print(f"起运时间：{yun.getStartSolar().toFullString().split()[0]}")