#!/usr/bin/env python
# coding: utf-8

# In[1]:


####Tianrui Lai####
#####Feb 2023#####


# In[2]:


# -*- coding: UTF-8 -*-
import os
import re
import sys
import shutil
import json
import xlwt, xlrd
import pandas as pd
#from pages_clubs2 import CITY_CLUBS

# In[3]:



# LIST_OF_TITLES is the building block for every single cleaning and match
# （）is to group the expressions; " in first and last place represents string; |is or; \the backward slash is Escape Character;
LIST_OF_TITLES = "(M\&M\"|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|Mim|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More)"


# EXPRESSIONS FOR CLEANING
# r represents original strings
#{1}is one re, {2,}is 2 or more re
# * is 0 or more; + is one or more
# goal: add space before and after parentheses
# include a group by (): can be used to extract later
PARENTHESES_AFTER_STRING = r"([A-Za-z]\()"
PARENTHESES_BEFORE_STRING = r"(\)[A-Za-z])"
SPACING_OF_HYPHENS = r"[a-z]*(\-)[A-Z]" # -Unv. to identify university

# goal: add space to split titles
TITLE_FIX_END_OF_PREV = fr"([A-Z]{1}[a-z]{2,}){LIST_OF_TITLES}"
TITLE_FIX_BEG_OF_NEXT = fr"{LIST_OF_TITLES}([A-Z]{1}[a-z]{1,})"

# EXPRESSIONS FOR DATASET FORMATION
# ^ in brackets: except; \s: any blanks; \b a word boundary, which is the position between a word character (as defined by \w) and a non-word character; ? is 0  or 1 time
# full name without parentheses: some character without blank+ title+ words without blank, hyphen and parentheses+ words without blank and parentheses
TITLE_DETECTION = rf"([^(\s]+)\b( {LIST_OF_TITLES} )([^(\s-]*?)( ([^(\s.]+)|([^(\s.]+)) "
PARENTHESES_DETECTION = r" (\w+) (\(+[A-Za-z ]{1,}\))"  # These two are for hh heads!!!
TITLE_DETECT_V2 = rf"([^(\s]+)\b( {LIST_OF_TITLES} )([A-Za-z ]*)"

WIFE_SURNAME_TWO_CAPITAL_LETTERS = r"( [A-Z] )([A-z][a-z]*)"
WIFE_WITHOUT_SPACES = r"([A-Z]{1}[a-z]*)[A-Z]{1}"
WIFE_HAS_MIDDLE_NAME = r"( [A-Z] )([A-z]{1}[a-z]*)"  # These are for fixing the stuff between parentheses, hence wives!

NEW_TITLE_DETECTION = "([^\s]+)\b( (M\&M\"|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More) )([A-Za-z ]*)( )?(\(([^\)\(]+)\))?"

# THIS ONE BELOW DOES NOT NEED TO HAVE SPACES BETWEEN TITLES, AND STILL WORKS IF THERE ARE MUTLIPLE SPACES!
#EXTREME_TITLE_DETECTION = r"([^(\s]+)\b( (M\&M\"|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More) )([A-Za-z ]*)( )?(\(([^)]+)\))?"
# r"([^(\s]+)\b( (M\&M\"|Mine|Lt\&M\"|M\&MW\"|MÃ†N\"\*|NÃ†N\"|Gen\&M\"|Gen\&M\'|Ct\&Ctss|Col\&Mâ€œ|Hon\&M\"|Hon\&M\*\*|Capt \& N\"|Capt\&N\"|Capt \& N\*\*|Col \& N\"|Brig Gen \& N\"|Maj \& M\*\*|Min|D&M\"\*|MIN\"|NEN\"|NAN\"|D&N\"|Niss|NAM\"|M&M'\*|N&N\"|NEM\"|M&M''|M&M\*\*|M&N|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More) )([A-Za-z ]*)( )?(\(([^)]+)\))?"

CORRECT_TITLES = {
    'Mr': ["M'", "N'", "M", "N", 'M-', "I'", '1*', 'Mº', 'Mr', 'N°','M'],
    'Mrs': ['Mrs','M"', "M's", 'MT', 'I"', 'M*', '1**', '1"', 'N"', 'M**', 'M".', 'Mrs', 'N**', 'I™', 'N™' "Mâ€œ",'M³'],
    'Mr&Mrs': ["Mr&Mrs",'M&M"', 'MIN"', 'NEN"','NAN"', 'NAM"', "M&M'*", 'N&N"', 'NEM"', "M&M''", "M&M**", 'M&N',
               'M&M"', 'MAN"', 'MEM"', "M&ME", "M&M*", 'M&M"*', 'MM"', 'M&M', 'N&MT', 'MIM"', 'MAM"', "'MN"
               'Mam"', 'N&M"', 'Man"', 'M.M"', "M&M™", 'MEN"', "MxM™", 'MEM*', 'M&N"', 'Män"', 'MIN"', 'MIM', 'MIN', 'NIN', 'NIM', 'MEM', 'NEM', 'MEN', 'NEN',
               'Mik"', 'Mom', 'W&M"', 'NIM"', 'Mim"', "M&MW", 'MÃ†N"*','NÃ†N"','MIN"', 'MIM"','NEN', 'NAN', 'NAM', 'MAN','MAM'],
    'Dr&Mrs': ['Dr&Mrs','D&M"*', 'D&N"', 'D&M"', 'D&M*', 'D&M', 'DÆM"', 'D&M**','DaN','Da N'],
    'Dr': ['Dr','D"', "D'"],
    'Miss': ['Min', 'Niss', 'Miss', 'Mis', 'Mo"', 'M8s', 'Mie','Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins', 'Viss','M¹'],
    'Misses': ['Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'lisses'],
    'Msrs': ['Msrs','Mi', 'Ms', 'Mb', 'Me', 'M***', 'Mens', 'Nissen'],
    'Lt&Mrs': ['Lt&Mrs','Lt&M"'],
    'Lt':['Lt'],
    'Gen&Mr': ["Gen&Mr","Gen&M'"],
    'Gen&Mrs': ["Gen&Mrs",'Gen&M"'],
    'Ct&Ctss': ['Ct&Ctss'],
    'Hon&Mrs': ["Hon&Mrs",'Hon&M"', 'Hon&M**'],
    'Capt&Mrs' : ['Capt&Mrs','Capt & N"', 'Capt&N"', 'Capt & N**'],
    'Maj&Mrs':['Maj&Mrs','Maj & M**'],
    'BrigGen&Mrs': ['BrigGen&Mrs','Brig Gen & N"'],
    'Col&Mrs':['Col&Mrs','Col & N"', 'Col&Mâ€œ'],
    'Rev':['Rev'],
    'Col':['Col'],
    'Capt':['Capt'],
    'Maj':['Maj']
}

HH_TITLES = ['Mr\\&Mrs', 'M\\&M"', 'MIN"', 'NEN"NAN"', 'NAM"', "M\\&M'\\*", 'N\\&N"', 'NEM"', "M\\&M''", 'M\\&M\\*\\*', 'M\\&N', 'M\\&M"', 'MAN"', 'MEM"', 'M\\&ME', 'M\\&M\\*', 'M\\&M"\\*', 'MM"', 'M\\&M', 'N\\&MT', 'MIM"', 'MAM"', 'Mam"', 'N\\&M"', 'Man"', 'M\\.M"', 'M\\&M™', 'MEN"', 'MxM™', 'MEM\\*', 'M\\&N"', 'Män"', 'MIN"', 'Mik"', 'Mom', 'W\\&M"', 'NIM"', 'Mim"', 'M\\&MW', 'MÃ†N"\\*', 'NÃ†N"', 'Dr\\&Mrs', 'D\\&M"\\*', 'D\\&N"', 'D\\&M"', 'D\\&M\\*', 'D\\&M', 'DÆM"', 'D\\&M\\*\\*', 'Lt\\&Mrs', 'Lt\\&M"', 'Gen\\&Mr', "Gen\\&M'", 'Gen\\&Mrs', 'Gen\\&M"', 'Ct\\&Ctss', 'Hon\\&Mrs', 'Hon\\&M"', 'Hon\\&M\\*\\*', 'Capt\\&Mrs', 'Capt\\ \\&\\ N"', 'Capt\\&N"', 'Capt\\ \\&\\ N\\*\\*', 'Maj\\&Mrs', 'Maj\\ \\&\\ M\\*\\*', 'BrigGen\\&Mrs', 'Brig\\ Gen\\ \\&\\ N"', 'Col\\&Mrs', 'Col\\ \\&\\ N"', 'Col\\&Mâ€œ']

JUNIOR_TITLES = ['Mr','Mrs','Miss','Misses',
                 'M¹','M³','MT', 'Ms', "M's", 'Mises', 'M\\*\\*\\*', 'N™Mâ€œ', 'Mis', 'I"', 'Ni', "I'", '1\\*', 'Me', 'Mrs', 'Mº', 'N"', 'N\\*\\*', 'Mie', 'M', 'Mr', 'Mama', 'N°', "M'", 'Mo"', '1"', 'Mins', 'Niss', 'Mi', "N'", 'lisses', 'Miss', 'M"', 'M\\-', 'M8s', 'Mens', 'Min', 'M\\*', 'M\\*\\*', 'Vi', 'Nisses', 'I™', 'Viss', 'Misé', 'N', 'Mies', 'Mine', 'M"\\.', 'Nissen', 'y', '1\\*\\*', 'Msrs', 'fis', 'Misses', 'Mb']

OTHER_TITLES = ['Mr', "M'", "N'", 'M', 'N', 'M\\-', "I'", '1\\*', 'Mº', 'Mr', 'N°', 'M', 'Mrs', 'Mrs', 'M"',"'MN",  "M's", 'MT', 'I"', 'M\\*', '1\\*\\*', '1"', 'N"', 'M\\*\\*', 'M"\\.', 'Mrs', 'N\\*\\*', 'I™', 'N™Mâ€œ', 'M³', 'Mr\\&Mrs', 'Mr\\&Mrs', 'M\\&M"', 'MIN"', 'MIM"','MIM', 'MIN', 'NIN', 'NIM', 'MEM', 'NEM', 'MEN', 'NEN', 'NAN', 'NAM', 'MAN', 'MAM', "M\\&M'\\*", 'N\\&N"', 'NEM"', "M\\&M''", 'M\\&M\\*\\*', 'M\\&N', 'M\\&M"', 'MAN"', 'MEM"', 'M\\&ME', 'M\\&M\\*', 'M\\&M"\\*', 'MM"', 'M\\&M', 'N\\&MT', 'MIM"', 'MAM"', 'Mam"', 'N\\&M"', 'Man"', 'M\\.M"', 'M\\&M™', 'MEN"', 'MxM™', 'MEM\\*', 'M\\&N"', 'Män"', 'MIN"', 'Mik"', 'Mom', 'W\\&M"', 'NIM"', 'Mim"', 'M\\&MW', 'MÃ†N"\\*', 'NÃ†N"', 'Dr\\&Mrs', 'Dr\\&Mrs', 'D\\&M"\\*', 'D\\&N"', 'D\\&M"', 'D\\&M\\*', 'D\\&M', 'DÆM"', 'D\\&M\\*\\*', 'Dr', 'Dr', 'D"', "D'", 'Miss', 'Min', 'Niss', 'Miss', 'Mis', 'Mo"', 'M8s', 'Mie', 'Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins', 'Viss', 'M¹', 'Misses', 'Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'lisses', 'Msrs', 'Mi', 'Ms', 'Mb', 'Me', 'M\\*\\*\\*', 'Mens', 'Nissen', 'Lt\\&Mrs', 'Lt\\&Mrs', 'Lt\\&M"', 'Lt', 'Lt', 'Gen\\&Mr', 'Gen\\&Mr', "Gen\\&M'", 'Gen\\&Mrs', 'Gen\\&Mrs', 'Gen\\&M"', 'Ct\\&Ctss', 'Ct\\&Ctss', 'Hon\\&Mrs', 'Hon\\&Mrs', 'Hon\\&M"', 'Hon\\&M\\*\\*', 'Capt\\&Mrs', 'Capt\\&Mrs', 'Capt\\ \\&\\ N"', 'Capt\\&N"', 'Capt\\ \\&\\ N\\*\\*', 'Maj\\&Mrs', 'Maj\\&Mrs', 'Maj\\ \\&\\ M\\*\\*', 'BrigGen\\&Mrs', 'BrigGen\\&Mrs', 'Brig\\ Gen\\ \\&\\ N"', 'Col\\&Mrs', 'Col\\&Mrs', 'Col\\ \\&\\ N"', 'Col\\&Mâ€œ', 'Rev', 'Rev', 'Col', 'Col', 'Capt', 'Capt', 'Maj', 'Maj']

ALL_TITLES = ['Mr', "M'", "N'", 'M', 'N', 'M\\-', "I'", '1\\*', 'Mº', 'Mr', 'N°', 'M', 'Mrs', 'Mrs', 'M"',"'MN", "M's", 'MT', 'I"', 'M\\*', '1\\*\\*', '1"', 'N"', 'M\\*\\*', 'M"\\.', 'Mrs', 'N\\*\\*', 'I™', 'N™Mâ€œ', 'M³', 'Mr\\&Mrs', 'Mr\\&Mrs', 'M\\&M"', 'DaN', 'Da N','MIN"', 'MIM"','MIM', 'MIN', 'NIN', 'NIM', 'MEM', 'NEM', 'MEN', 'NEN', 'NAN', 'NAM', 'MAN', 'MAM', "M\\&M'\\*", 'N\\&N"', 'NEM"', "M\\&M''", 'M\\&M\\*\\*', 'M\\&N', 'M\\&M"', 'MAN"', 'MEM"', 'M\\&ME', 'M\\&M\\*', 'M\\&M"\\*', 'MM"', 'M\\&M', 'N\\&MT', 'MIM"', 'MAM"', 'Mam"', 'N\\&M"', 'Man"', 'M\\.M"', 'M\\&M™', 'MEN"', 'MxM™', 'MEM\\*', 'M\\&N"', 'Män"', 'MIN"', 'Mik"', 'Mom', 'W\\&M"', 'NIM"', 'Mim"', 'M\\&MW', 'MÃ†N"\\*', 'NÃ†N"', 'Dr\\&Mrs', 'Dr\\&Mrs', 'D\\&M"\\*', 'D\\&N"', 'D\\&M"', 'D\\&M\\*', 'D\\&M', 'DÆM"', 'D\\&M\\*\\*', 'Dr', 'Dr', 'D"', "D'", 'Miss', 'Min', 'Niss', 'Miss', 'Mis', 'Mo"', 'M8s', 'Mie', 'Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins', 'Viss', 'M¹', 'Misses', 'Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'lisses', 'Msrs', 'Mi', 'Ms', 'Mb', 'Me', 'M\\*\\*\\*', 'Mens', 'Nissen', 'Lt\\&Mrs', 'Lt\\&Mrs', 'Lt\\&M"', 'Lt', 'Lt', 'Gen\\&Mr', 'Gen\\&Mr', "Gen\\&M'", 'Gen\\&Mrs', 'Gen\\&Mrs', 'Gen\\&M"', 'Ct\\&Ctss', 'Ct\\&Ctss', 'Hon\\&Mrs', 'Hon\\&Mrs', 'Hon\\&M"', 'Hon\\&M\\*\\*', 'Capt\\&Mrs', 'Capt\\&Mrs', 'Capt\\ \\&\\ N"', 'Capt\\&N"', 'Capt\\ \\&\\ N\\*\\*', 'Maj\\&Mrs', 'Maj\\&Mrs', 'Maj\\ \\&\\ M\\*\\*', 'BrigGen\\&Mrs', 'BrigGen\\&Mrs', 'Brig\\ Gen\\ \\&\\ N"', 'Col\\&Mrs', 'Col\\&Mrs', 'Col\\ \\&\\ N"', 'Col\\&Mâ€œ', 'Rev', 'Rev', 'Col', 'Col', 'Capt', 'Capt', 'Maj', 'Maj']


NAME_ABBRV ={
    "Wm": "William",
    "Robt": "Robert",
    "Rob't": "Robert",
    "Rob": "Robert",
    "Ed": "Edward",
    "Eug": "Eugene",
    "Rich": "Richard",
    "Dan": "Daniel",
    "Edw": "Edward",
    "Ch": "Charles",
    "Chas": "Charles",
    "Geo": "George",
    "Hy": "Henry",
    "Jas": "James",
    "Benj": "Benjamin",
    "Georgeh": "George",
    "Howardr": "Howard",
    "Thos": "Thomas",
    "Thomasf": "Thomas",
    "Johnh": "John",
    "Johnr": "John",
    "Jos": "Joseph",
    "Sm": "Samuel",
    "Arch": "Archibald",
    "Rich'd": "Richard",
    "Fred'k": "Frederick",
    "Fred'c": "Frederic",
    "Sr" : "Senior"
 }

CORRECT_ADDRESS = {
    '10': ['I\s*O'],
    '110':['I\s*IO','I\s*10'],
    '111': ['I\s*II'],
    '11': ['I\s*I'],
    '1110':['I\s*I\s*I\s*O'],
    '101':['I\s*OI'],
    '120':['I\s*20'],
    '190':['I\s*9\s*o'],
    '00':['\s*O\s*O\s*'],
    'I11':['Ill'],
    '1':['\sI\s'],
    '0':['\sO\s'] 
}

# The very first name: title (EG: Mrs. Mr. Dr. Rev.) + name; or name; or title (EG: dr) + name; group(1)
base_pattern = '(^[A-IK-Z][a-z][a-z]? [A-Z][a-z]+|^[A-Z][a-z]+|^[dv][aeuo][nr]? [A-Z][a-z]+) ('
# General expressions to match titles; group(2)
title_patterns = ['[\w ]+Col ?& ?\S+', '[A-Z0-9]+\W+', '[A-Z][a-z]\W+', '[A-Z][a-z][a-z]\W+', '[A-Z][a-z]* ?& ?\S+',
                  '[A-Z][A-z][A-z]\W+[A-Z]+', '[A-Z][a-z]+\W+ Mrs ', '[A-Z][a-z][a-z] ?[\&A-Z]+\W',
                  '\S+â€œ', '\S+â€™', '\S+â€', '\S+¢', 'Lt','Mr', 'Mrs', 'Miss', 'Mom', 'Misses', 'Capt', 'M', 'N', 'Mis',
                  '[^\w\.]+', '\\\"','[MNV][a-z]',"fis", 'Viss', 'Maj Gen', 'Maj', 'Capt\S+',
                  'Mises', 'Col', 'Rev', '[A-Z][a-z][a-z] ?[\&A-Z]+[a-z]?\W+[A-Z]+[a-z]?', 'Mia', 'lisses', 'Ms', '[A-Z][a-z][A-Z]\W+', 'Mama', 'y', '[A-z]y', 'Y',
                  'Mi[a-z][a-z]', '\w\W+', '[A-Z]\W+[A-Z]', "Nisses", "[\'\"]?[MN]{1,2}[\'\"]?",
                  '[A-Z][a-z][A-Z][a-z]', '[A-Z][A-Z]', 'flases','[MNVH][iao][easn]', '[A-Z][a-z][a-z]? ?[\&A-Z]+[a-z]+\W+[A-Z]+[a-z]?\W?\W?',
                  '[A-Z][a-z]\W+[A-Z][a-z][a-z][a-z]','[A-z]+[^\w ]+[A-z]+\W+','M I M','MIM']
full_pattern = base_pattern +'|'.join(title_patterns) + '|'.join(ALL_TITLES) + ')'
full_and_spouse_name = " ([A-Za-z ]+(?=[A-Z][a-z][a-z]?\.)|[A-Za-z ]*\*?)(( )?(\(([A-z \-']+)\)))?"
full_name = "([A-Za-z ]+(?=[A-Z][a-z][a-z]?\.)|[A-Za-z ]+\*?)"
# The full titles including household's name and wife's name
# xxx(?=pattern): match the whole xxxpattern, but only catch xxx; 
# (multiple)name separate with spaces+ (optional) a word with 2-3 letters end with .; or a sequence of zero or more letters or spaces, followed by an optional asterisk character
#+ (optional) space+ (optional)name &- &' in parentheses
# group(3) = household name after title, group(4)= wife name including space and patentheses, group(7)= wife name in parentheses
EXTREME_TITLE_DETECTION = full_pattern + full_and_spouse_name
junior = "([jJ][pniourgsl]+|There) "
TITLE_PATTERNS = '('+ '|'.join(title_patterns) +')'
HH_TITLE = '('+ '|'.join(HH_TITLES) +')'
JUNIOR_TITLE = '('+ '|'.join(JUNIOR_TITLES) +')'
#full_name = "(\b\w+)(\b\w+)+"
JUNIOR_DETECTION = '('+junior + '(('+ '|'.join(JUNIOR_TITLES) +') )' + full_name +')' + '(& (('+ '|'.join(JUNIOR_TITLES) + ') )?'+ full_name + ')?'+ '(& (('+ '|'.join(JUNIOR_TITLES) + ') )?'+ full_name + ')?'
OTHER_DETECTION = '^(\s*)' + '(' + '|'.join(OTHER_TITLES) + ')' + full_and_spouse_name
ADDRESS_DETECTION = "(([\.]{2,}|[\. ]{2,})(.*)([A-Za-z-0-9\s]+))"
ADDRESS_DETECTION_EXACT = "(\w[ ]*[0-9]{1,3}[ ]*[A-Z][ ]*[0-9]{1,3}|[0-9]{1,3}[ ]*[A-Z][ ]*[A-Za-z-]|[0-9]{1,4}[ ]*[A-Za-z-]+\s?[A-Za-z-]+[ ]*Sq|[0-9]{1,4}[ ]*[A-Za-z-]+\s?[A-Za-z-]+[ ]*St[ ]*[A-Za-z-]+\s?[A-Za-z-]+|[0-9]{1,4}[ ]*St[A-z]+|[0-9]{1,4}[ ]*[A-Za-z-]+\s?[A-Za-z-]+[ ]*Av|[0-9]{1,3}.+NY|[0-9]{1,3}.+NJ|[0-9]{1,3}.+DC|[0-9]{1,3}.+N Y|[0-9]{1,3}.+N J)"
NAME_ADDRESS_DETECTION = EXTREME_TITLE_DETECTION + '(.*)' + ADDRESS_DETECTION
NAME_ADDRESS_DETECTION_EXACT = EXTREME_TITLE_DETECTION + '(.*)' + ADDRESS_DETECTION_EXACT
FOREIGN_DETECTION = EXTREME_TITLE_DETECTION + "(.+)(London|Rome|Paris|Italy|France |Germany|Ireland)"
FOREIGN = "(London|Rome|Paris|Italy|France|Germany|Ireland|Eng)"
DEATHECTION = EXTREME_TITLE_DETECTION + "(.+)(Died)"
TIME = "(=?.*)(Jan|Feb|Mar|Mch|Mcn|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)([a-z]*)(\s*)([0-9]{1,2})?"
TRIVIAL = "\-|'{2,}|\"|\||^I\s|\[|\."
NONASCII = "[^A-z0-9\s\']+"
PHONE  = "([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|Dhone  Ph|No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|Phon|phop|Phone|phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|po|op|no|ne|P| o|p|e|g|i|f|w|d|r)(\s*)([0-9]+[A-Za-z]*)(\s*)(f Mt V|k Mt V|Mt V|W Mt V|IO W|B B |Tux)"
PHONE2  = "([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|Dhone  Ph|No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|Phon|phop|Phone|phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|po|op|no|ne|P| o|p|e|g|i|f|w|d|r)(\s*)([0-9]+[A-Za-z]*)"
PHONE3 = "^([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|Dhone  Ph|No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|Phon|phop|Phone|phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|ne|P| o|p|po|op|no|g|e|ho|i|f|w|d|r|u|V|Q|j|J|f Mt V|k Mt V|Mt V|W Mt V|IO W|B B |Tux|Pros)\s+"
PHONE4 = "^([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|Dhone  Ph|No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|Phon|phop|Phone|phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|ne|P| o|p|po|op|no|g|e|ho|i|f|w|d|r|u|V|Q|j|J|f Mt V|k Mt V|Mt V|W Mt V|IO W|B B |Tux|Pros)$"
OTHER = "Died.*|sa tog|Club"
OTHER2 = "^(')?\s*\w+\s*$|^\s*\d+\s*$"
ELSE = "absent|Absent|abroad|Abroad|Ab'd|avd|abd|Av'd|av'd|ab'd|at'l|atl"
MOVE = "(see)(.*)|(See)(.*)"
BRACKET = "「|」|\["
# The line belongs to previous line
LINE_AFTER_PREV = "^\(.*\)|^(\s*(\.)+)|^(\s*(\. )+)|^(\s*[0-9]+)|^(\s*Uv(\.)?)|^(\s*Un\.)|^(\s*Ui(\.)?)|^(\s*UI(\.)?)|^(\s*Rf(\.)?)|^(\s*Ph(\:)?\s*[0-9])|^(\s*Mc\.)|^(\s*Md\.)|^(\s*Cy\.)|^(\s*Php(\:)?\s*[0-9])|^(\s*Y')|^(\s*Pho(\:)?\s*[0-9])|^(\s*P\s*[0-9])"
next_line_club = r"^[A-Z][a-z](?=\.)|^[A-Z][a-z][a-z](?=\.)|^[A-Z]+\'|^(?<=[A-Z]\')[0-9]+|^[A-Z]+(?=\.)|^[^\(\[]+\)|^\.|^ \."
next_line_other = r"(London|Rome|Paris|Italy|England|France|Germany|Ireland|Died)"

CITY_CLUBS={'New York': {'A': 'Authors', 'Ad': 'Alpha Delta Phi', 'Al': 'Aldine', 'Ay': 'American Yacht', 'Bk': 'Brooklyn', 'C': 'Century', 'Cal': 'Calumet', 'Cn': 'Corinthian Yacht', 'Ct': 'City', 'Cth': 'Catholic', 'Cy': 'Country', 'Dke': 'Delta Kappa Epsilon', 'Dp': 'Deepdale Golf', 'Dt': 'Down Town', 'Du': 'Delta Upsilon', 'Dv': 'Deutscher Verein', 'E': 'Essex of Newark', 'Ec': 'Essex Co Country', 'Country': '', 'Eg': 'Engineers', 'Fn': 'Fencers', 'G': 'Grolier', "H'": 'Harvard Graduate', 'Ha': 'Hamilton of Brooklyn', 'K': 'Knickerbocker', 'L': 'S Lawyers', 'La': 'Ladies', 'Lc': 'Larchmont Yacht', 'LI': 'Loyal Legion', 'Lt': 'Lotos', 'M': 'Manhattan', 'Ma': 'Manhattan Athletic', 'Mb': 'Meadow Brook', 'Me': 'Merchants', 'Mo': 'Morristown', 'Mt': 'Metropolitan', 'N': 'New York', 'Na': 'NY Athletic', 'Ny': 'N Y Yacht', "P'": 'Princeton Graduate', 'Pl': 'Players', 'R': 'Racquet & Tennis', 'Rh': 'Rockaway Hunting', 'Rf': 'Reform', 'Rg': 'Riding', 'Rp': 'Republican', 'Rv': 'Sons of Revolution', '8': 'St Nicholas', 'Yacht': '', 'Sa': 'St Anthony', 'Anthony': '', 'Nicholas': '', 'Sp': 'Southern Society', 'Ss': "South Side Sportsmen's", 'Sv': 'Seventh Veteran', 'T': 'Tuxedo', 'Un': 'Union', 'UI': 'Union League', 'Us': 'United Service', 'U': 'Union College Graduate', 'Uv': 'University', 'Uva': 'University Athletic Club', 'W': 'Whist', 'Wk': 'Westminster Kennel', "Y'": 'Yale Graduate', 'Zp': 'Zeta Psi', "Aht'": 'Amherst Graduate', 'Bd': 'Barnard', "Br'": 'Brown University Graduate', 'Ch': 'Church', "Cl'": 'Columbia Graduate', 'On': 'Corinthian Yacht', 'Col': 'Colonial', 'Cw': 'Society of Colonial Wars', 'Dm': 'Democratic', 'Hl': 'Holland Society', "N'": 'New York University Graduate', "Pn'": 'University of Pa Graduate', 'S': 'Seawanhaka Cor Yacht', 'Bn': 'St Nicholas', 'Bp': 'Baltusrol Golf Club', 'Bs': 'South Side', "Ty'": 'Trinity Graduate', "U'": 'Union League', "Wms'": 'Williams Graduate', 'Ag': 'St Andrews Golf Club', "Ant'": 'Amherst Graduate', 'Bg': 'Baltusrol Golf', 'Cc': 'Society of Cincinnati', 'Cd': 'Colonial Dames', 'CF': 'Columbia Graduate', 'Co': 'Corinthian Yacht', 'Rn': 'Rockaway Hunt', 'Sg': 'St Andrews Golf', 'Sn': 'St Nicholas', 'So': 'Southern Society', 'Andrews': 'Golf Club', 'Br': 'Brown University Gittduate', 'CP': 'Columbia Graduate', 'Or': 'Cornell Graduate', 'Ot': 'City', 'Dar': 'Daughters of American Revolution', 'Dth': 'Dartmouth Graduate', 'Jkl': 'Jekyl Island Club', 'Mg': 'Morris County Golf', 'Mtw': 'Metropolitan of Washington', 'Pr': 'Piping Rock', 'Pu': 'Psi Upsilon', 'Sue': 'St Nicholas Society', 'USA': 'USN U S Army Navy Uv University', 'An': 'Army & Navy', 'Wt': 'Society War of 1812', 'Ar': 'Sons of American Revolution', "Bow'": 'Bowdoin Graduate', '0': 'Century', 'Ce': 'Cincinnati Society', "Cr'": 'Cornell Graduate', "Dth'": 'Dartmouth Graduate', "Ham'": 'Hamilton Graduate', "Hob'": 'Hobart Graduate', "J'Hop'": 'Johns Hopkins Graduate', 'Mil': 'Military', 'Myf': 'Mayfiower Descendants', 'P': 'Princeton University Club', "Rens'": 'Rensselaer Polytechnic Graduate', 'Rensselaer': 'Polytechnic Ins Graduata Rf Reform', "Rut'": 'Rutgers Graduate', 'Snc': 'St Nicholas Society', 'Uac': 'University Athletic Club', 'Anf': 'Amherst Graduate', 'Ats': 'National Arts', 'Cda': 'Colonial Dames of America', 'De': 'Daughters of Cincinnati', 'Ft': 'Field & Turf', 'Fw': 'Foreign Wars Military Order of', 'H': 'Harvard University Club', 'Id': 'Manhattan', 'Upt': 'Uptown', 'U S N': 'US Army Navy', 'U S A': 'US Army Navy', 'As': 'Ardsley', 'Kg': 'Knollwood Country', 'SI': 'Strollers', 'Sne': 'St Nicholas Society', 'Tf': 'Turf & Field', "Tv'": 'Trinity Graduate', 'Bm': 'Badminton', 'Calumet': '', 'Ht': 'Huguenot Society', 'Jjt': 'Lotus', 'Merchants': '', 'PL': 'Players', 'Pa': 'University of Pa Graduate', 'St': 'Anthony', 'Sl': 'Strollers', 'University': '', 'J': "Hop' Johns Hopkins' Graduate", 'ZP': 'Zeta Psi', 'Au': 'Automobile of America', 'Ba': 'Barnard', 'Lb': 'Lambs', 'Mid': 'City Midday', 'Rc': 'Richmond County Country', 'Ty': 'Trinity Graduate', "Wins'": 'Williams Graduate', 'Cl': 'Columbia University Club', 'Cr': 'I Cosmopolitan', 'Gg': 'Garden City Golf', 'Hob': 'Hobart Graduate', 'Lo': 'Larchmont Yacht', 'Jwc': 'Merchants', "Pa'": 'University of Pa Graduate', 'SS': 'South Side', 'Y': 'Yale University Club', 'Ap': 'Apawamis', 'Ao': 'Aero', 'Ato': 'National Arts', 'II': 'Harvard University Club', 'Tv': 'Trinity Graduate', 'B': 'The Brook', 'Ll': 'Loyal Legion', "Cf'": 'Cornell Graduate', 'Iki': 'Jekyl Island Club', 'Cly': 'Colony', 'Dkc': 'Delta Kappa Epsilon', 'Kp': 'Zeta Psi', "IL'": 'H Graduate', 'Tkl': 'Jekyl Island Club', 'Rens': "Rensselaer Poly'tnc Ins Graduate", 'Wp': 'Whippany River', 'Rm': 'Rumson Country', 'Se': 'St Elmo', 'Wlc': 'Westminster Kennel', 'Rut': 'Rutgers Graduate', 'Elmo': '', 'US': 'Aor U SN US Army Navy Uv University', 'Sh': 'Sleepy Hollow Country', 'Sq': 'Squadron A Club', 'Dh': 'Daughters of Holland Dames', 'Snd': 'St Nicholas Society', 'Ker': 'Knnllwnnd', 'Wma': 'Williams Graduate', 'Generated': 'Harvard Univer 2021 1 10 42 GMT 2027 Jb6 31498', 'Public': 'Domain Google I', 'Cs': 'Cosmopolitan', 'Ef': 'Essex Fox Hounds', 'Hv': 'Harvard Graduate', 'Lm': 'Colonial Lords of Manors', 'Ns': 'Nassau Country', 'Uc': 'Union Society of Civd War', "USA'": 'West Point Graduate', 'Wms': 'Williams Club', 'Eo': 'Essex Co Country', 'Efl': 'Essex Fox Hounds', 'Jekyl': 'Island Club', 'Z': 'Knickerbocker', 'Ng': 'National Golf Links', 'Uvi': 'University', 'CT': 'Columbia Graduate', 'Jk': 'Jekyl Island Club', "USN'": 'Annapolis Graduate', 'Mit': 'Mass Institute Technology', 'Union': 'College Graduate', 'AF': 'Arm Francaise', 'BA': 'British Army', 'Ih': 'India House', 'Ln': 'Links', 'Lg': 'Links Golf', "Mit'": 'Mass Institute Tech Graduate', "Nc'": 'City of N Y College Graduate', "Nu'": 'New York University Graduate', 'I': '', 'USM': 'US Marine Corps', "Ht'": 'Harvard Graduate', 'Institute': 'Tech Graduate', 'Ok': 'Oakland Golf', 'Yk': 'York', 'City': '', 'Hi': 'Holland Soc', 'Lr': 'Links Golf', 'Nu': 'L New York University Graduate', 'Wn': 'Williams Club', 'JI': 'Iunior League', 'Pg': 'The Pilgrims', 'Cai': 'Calumet', 'Ck': 'Creek', "CI'": 'Columbia Graduate', 'CI': 'Columbia University Club', 'Revolution': '', 'HI': 'Holland Society', 'Hr': 'Hangar', 'Jl': 'Junior League', 'Le': 'Larchmont Yacht', 'Ned': "Nat'l Socy Colonial Dames", 'Re': 'Richmond County Country'}, 'Boston': {'Al': 'Algonquin', 'At': 'Athletic', 'Cy': 'Country', 'Ec': 'Essex County', 'Ex': 'Exchange', 'Ey': 'Eastern Yacht', 'My': 'Myopia Hunt', 'P': 'Puritan', 'Sb': 'St Botolph', 'Botolf': '', 'Sm': 'Somerset', 'Tv': 'Tavern', 'Ub': 'Union Boat', 'Un': 'Union', 'Uv': 'University', 'A': 'Art', 'Cr': 'Corinthian Yacht', 'Myf': 'Society of Mayflower Descendant', 'Nh': 'Norfolk Hunt', 'Botolph': '', 'Tr': 'Tennis & Racquet', 'Au': 'Automobile', 'Hn': 'Harvard of N Y', 'Ok': 'Oakley Country', 'Ee': 'Essex County Country', '8': 'Somerset', "Aht'": 'Amherst Graduate', "Br'": 'Brown Graduate', "Cl'": 'Columbia Graduate', "Dth'": 'Dartmouth Graduate', "H'": 'Harvard Graduate', "Mass'": 'Mass Inst of Tech Graduate My Myopia', "P'": 'Princeton Graduate', "Wms'": 'Williams Graduate', "Y'": 'Yale Graduate', 'Cl': 'Columbia Graduate', 'Rg': 'New Riding', 'Mit': 'Mass Inst of Tech Graduate', "CI'": 'Columbia Graduate', "Mit'": 'Mass Inst of Tech Graduate', 'Ch': 'Chilton', "Abt'": 'Amherst Graduate', 'Br': 'Brown Graduate', 'H': 'Harvard Club', 'May': 'Mayflower Club', 'I': '', 'FT': 'Harvard Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'Mfl': 'Mayflower Club', 'AF': 'Arm Francaise', 'BA': 'British Army', 'Y': 'Yale Graduate'}, 'Chicago': {'At': 'Athletic', 'Cal': 'Calumet', 'Cg': 'Chicago Golf', 'Ch': 'Chicago', 'Fl': 'Fellowship', 'Ft': 'Fortnightly', 'Ill': 'Illinois', 'Irq': 'Iroquois', 'Lt': 'Literary', 'On': 'Onwentsia', 'Sc': 'Saddle & Cycle', 'Tc': 'Twentieth Century', 'UI': 'Union League', 'Un': 'Union', 'Uv': 'University', 'Wn': "Woman's", 'Wp': 'Washington Park', 'Generi': 'Harvard University 2021 12 12 19 26 GMT 2027 hn4', 'Pubi': 'Domain Google 0 g0 0', 'Exc': 'Exmoor Country', 'Et': 'Fortnightly', 'DI': 'Illinois', 'Cm': 'Onwentsia', 'Be': 'Saddle & Cycle', 'Athletic': '', 'Cd': 'Colonial Dames', 'Dar': 'Daughters of American Revolution', 'Gv': 'Glen View', 'Md': 'Midlothian Country', "Alit'": 'Amhnrrt Graduata', "Br'": 'Brown Univ Graduate', "Cl'": 'Columbia Univ Graduate', 'Exo': 'Exmoor Country', "H'": 'Harvard Univ Graduate', "Hob'": 'Hobart College Graduate', 'LI': 'Loyal Legion', "Pa'": 'Univ of Penn Graduate', "Y'": 'Yale Univ Graduate', 'Aht': 'Amherst Graduate', 'Wm': "Woman's", 'Cda': 'Colonial Dames of America', 'Cw': 'Society of Colonial Wars', 'Hob': 'Hobart College Graduate', 'Ss': 'South Shore Country', 'Um': 'Union', "Aht'": 'Amherst Graduate', "Ch'": 'Univ of Chicago Graduate', 'Wat': "Woman's Athletic", 'Cl': 'Columbia Univ Graduate', 'Cc': 'Society of the Cincinnati', "^ob'": 'Hobart College Graduate', 'Cx': 'Caxton', 'Ev': 'Evanston Country', 'Lg': 'Lake Geneva Country', 'Br': 'Brown Univ Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'Y': 'Yale Univ Graduate', 'Public': 'Domain Org Jse', 'Cs': 'Casino', 'Pt': 'Fortnightly', 'Fy': 'Friday', 'Ih': 'Indian Hill'}, 'Philadelphia': {'A': 'Art', 'Ac': 'Acorn', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', 'Op': "Colonial Soc'y of Pa", 'Cr': 'Corinthian Yacht', 'Cw': 'Colonial Wars Cy Phila Country', 'Cy': 'Phil Country', 'Dar': 'Daughters of American Revolution', 'Gc': 'Germantown Cricket', "H'": 'Harvard Graduate', "Hav'": 'Haverford Graduate', 'Hg': 'Huntingdon Valley Golf', 'L': 'Lawyers', 'LI': 'Loyal Legion', 'Me': 'Merion Cricket', 'Mf': 'Manufacturers', 'Mk': 'Markham', "P'": 'Princeton Club', 'Nc': 'New Century', "Pa'": 'Univ of Penn Graduate', 'Pb': 'Philadelphia Barge', 'Pc': 'Philadelphia Cricket', 'Ph': 'Philadelphia', 'Pn': 'Penn Club', 'R': 'Rittenhouse', 'Rb': 'Rabbit', 'Be': 'Racquet', 'Rd': "Radnor' Hunt", 'Rv': 'Sons of Revolution', 'Sa': 'St Anthony', 'Sdg': 'Sedgeley', 'Ssk': 'State Schuylkill', 'UI': 'Union League', 'Uv': 'University', 'Uvb': 'University Barge', 'Wt': 'Society War of 1812', "Y'": 'Yale Graduate', 'Cc': 'Society of the Cincinnati', 'Cp': 'Colonial Society of Pa', 'Myf': 'Society of Mayflower Descendants', 'Rc': 'Racquet', 'Ii': 'Lawyers', 'Il': 'Rittenhouse', 'M': 'Manufacturers', "'": 'Myf Mayflower', 'S': '', 'H': 'Graduate of Harvard', 'Hav': 'Graduate of Haverford', 'Y': 'Yai Graduate', 'Anthony': '', 'So': 'Southern Club', 'Cywl': 'Country of Wilmington', 'Wil': 'Wilmington', 'Lm': 'La Moviganta KI', 'Rh': 'Rose Tree Fox Hunt', 'Fi': 'Franklin Inn', 'Pi': 'Franklin Inn', 'Hv': 'Huntingdon Valley Country', 'Pa': 'Univ of Penn Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'Dari': 'Daughters of American Revolution', 'Society': 'of Mayflower Descendants', 'Fw': 'Military Order of Foreign Wars', 'Ui': 'Union League', 'AF': 'Arm Francaise', 'BA': 'British Army', 'Aa': 'Art Alliance'}, 'San Francisco': {'Ath': 'Athenian Nile of Oakland', 'Bhm': 'Bohemian', 'Bur': 'Burlingame Country', "Cal'": 'Univ of California Graduate', 'Cos': 'Cosmos', 'Eb': 'Ebell of Oakland', 'Fmy': 'Family', "H'": 'Harvard Graduate', 'Hm': 'Home of Oakland', 'Pcu': 'Pacific Union', 'Sfg': 'San Francisco Golf', "Stan'": 'Stanford Univ Graduate', 'Ut': 'University', "Y'": 'Yale Graduate', 'Yv': 'Yniversity', 'Uv': 'University', 'Ebell': 'of Oakland', 'Cal': 'Univ of California Graduate', 'Fr': 'Francisca', 'H': 'Harvard Graduate', 'He': 'Holluschickie', 'Oly': 'Olympic', 'Tc': 'Town & Country', 'Y': 'Yale Graduate', 'Bhin': 'Bohemian', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', 'Cw': 'Society of Colonial Wars', 'Dar': 'Daughters of American Revolution', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', "C^l'": 'Univ of California Graduate', 'Cv': 'Society of Colonial Wars', "Fmy'": 'Family', 'Clt': 'Claremont Country', 'C': 'Century'}, 'Washington': {'Abi': 'Alibi', 'An': 'Army & Navy', 'C': 'Century', 'Cd': 'Colonial Dames', 'Cos': 'Cosmos', 'Cvc': 'Chevy Chase', 'Mt': 'Metropolitan', 'Rv': 'Sons of Revolution', 'Wg': 'Washington Golf & Country', 'Wh': 'Washington', "Aht'": 'Amherst Graduate', "Br'": 'Brown Graduate', 'Cda': 'Colonial Dames of America', 'Cy': 'Country', "Dth'": 'Dartmouth Graduate', "H'": 'Harvard Graduate', "Ham'": 'Hamilton Graduate', "Hob'": 'Hobart Graduate', 'J': "Hop' Johns Hopkins Graduate", 'Pa': 'Univ of Penn Graduate', "Ty'": 'Trinity Graduate', "Y'": 'Yale Graduate', "Abt'": 'Amherst Graduate', "Hap'": 'Hamilton Graduate', "Pa'": 'Univ of Penn Graduate', 'A': 'Alibi', 'Uv': 'University', 'Br': 'Brown Graduate', 'Cc': 'Society of the Cincinnati', 'Cw': 'Society of Colonial Wars', 'LI': 'Loyal Legion', 'P': 'Princeton Univ Graduate', 'Ty': 'Trinity Graduate', 'Wt': 'Society of War of 1812', 'Ar': 'Sons of American Revolution', "P'": 'Princeton Univ Graduate', 'DEC': '311907', 'Aht': 'Amherst Graduate', 'H': 'Harvard Graduate', "LHop'": 'Johns Hopkins Graduate', 'Ll': 'Loyal Legion', 'Rg': 'Riding & Hunt', 'Y': 'Yale Graduate', 'Ham': "Hamilton' Graduate", "Cl'": 'Columbia Graduate', "Geo'": 'Georgetown Graduate', 'Geo': "W' George Washington Graduate", "USA'": 'I', "USN'": 'I of West Point Annapolis', 'Abh': 'Alibi', 'Dth': 'Dartmouth Graduate', 'AU': 'Metropolitan', "Cln'": 'Columbian Graduate', 'AF': 'Arm Francaise', 'BA': 'British Army', 'Rc': 'Racquet', 'USM': 'US Marine Corps', 'Wn': 'Washington'}, 'Baltimore': {'Ath': 'Athenaeum', 'Be': 'Bachelor Cotillion', 'Bl': 'Baltimore', 'Cc': 'Cincinnati Society', 'Cda': 'Colonial Dames of America', 'Cy': 'Baltimore Country Club', 'Elk': 'Elkridge Club', 'Jrc': 'Junior Cotillion', 'Me': 'Merchants', 'Md': 'Maryland', 'Uv': 'University', 'Al': 'Arundel', 'Gv': 'Green Spring Valley Hunt', 'J': "Hop' Johns Hopkins Graduate", "Aht'": 'Amherst Graduate', "Br'": 'Brown Univ Graduate', "Cl'": 'Columbia Univ Graduate', "H'": 'Harvard Univ Graduate', "Hob'": 'Hobart Univ Graduate', "P'": 'Princeton Graduate', "Pa'": 'Univ of Penn Graduate', "Ty'": 'Trinity Graduate', "Y'": 'Yale Univ Graduate', '8': '', 'Aht': 'Amherst Graduate', 'Dar': 'Daughters of American Revolution', 'P': 'Princeton Graduate', 'Pa': 'Univ of Penn Graduate', 'Y': 'Yale Univ Graduate', "J'Hop'": 'Johns Hopkins Graduate', "J'": 'Hop Johns Hopkins Club', 'Cd': 'Colonial Dames', 'H': 'Harvard Univ Graduate', "Uv'": 'University', 'Br': 'Brown Univ Graduate', 'Cl': 'Columbia Univ Graduate', 'Rv': 'Sons of Revolution', 'Ahl': 'Amherst Graduate', 'Hob': 'Hobart Univ Graduate', 'Ty': 'Trinity Graduate', "USA'": 'West Point Graduate', "USN'": 'Annapolis Graduate', 'Bc': 'Bachelors Cotillon', 'Cw': 'Society of Colonial Wars', 'Gi': 'Gibson Island', 'Ned': "Nat'l Soc'y Colonial Dames", 'T': 'Town', 'Mv': 'Mt Vernon Town', "CI'": 'Columbia Univ Graduate'}, 'Buffalo': {'Bf': 'Buffalo', 'Ca': 'Canoe', 'Cw': 'Colonial Wars', 'Cy': 'Country', 'Dar': 'Daughters of American Revolution', 'El': 'Ellicott', 'Fl': 'Falconwood', 'Hl': 'Holland Society', 'Lb': 'Liberal', 'Rv': 'Sons of Revolution', 'St': 'Saturn', 'Tc': 'Twentieth Century', 'Ar': 'Sons of American Revolution', 'Bfg': 'Buffalo Golf', "Cl'": 'Columbia Graduate', 'G': 'Garret', "H'": 'Harvard Graduate', 'LI': 'Loyal Legion', "P'": 'Princeton Graduate', 'Uv': 'University', "Y'": 'Yale Graduate', 'Cl': 'Columbia Graduate', "Cr'": 'Cornell Graduate', 'LL': 'Loyal Legion', 'Pk': 'Park', 'Y': 'Yale Graduate', 'H': 'Harvard Club', 'Myf': 'Mayflower Descendants', 'Cr': 'Cornell Graduate', 'Cri': 'Cornell Graduate', 'V': 'Yale Graduate', 'Columbia': 'Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', "CI'": 'Columbia Graduate', "G'": 'Country', 'P': 'Princeton Graduate'}, 'Cleveland': {'Bz': 'Buz Fuz Dayton', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', 'Cg': 'Cincinnati Golf', "Cl'": 'Columbia Graduate', 'Cm': 'Commercial Cincinnati', "Cr'": 'Cornell Univ Graduate', 'Cw': 'Colonial Wars', 'Cy': 'Country', 'Dar': 'Daughters of American Revolution', 'De': 'Dayton Country', 'Dy': 'Dayton', "H'": 'Harvard Graduate', "Ham'": 'Hamilton Graduate', "P'": 'Princeton Graduate', 'Qc': 'Queen City Cincinnati', 'Rg': 'Riding Cincinnati', 'Rv': 'Sons of the Revolution', 'U': 'University', "Wr'": 'Western Reserve Graduate', "Y'": 'Yale Graduate', 'Ar': 'Sons of American Revolution', 'Cl': 'Colonial', 'Euc': 'Euclid', 'Rd': 'Roadside', 'Tv': 'Tavern', 'Un': 'Union', 'Uv': 'University', 'Cr': 'Columbia Graduate', 'Yale': 'Graduate', 'Po': 'Polo', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis Uv University', 'May': 'Mayfield Country', 'P': 'Princeton Graduate', 'Wr': 'Western Reserve Graduate', 'Y': 'Yale Graduate', 'H': 'Harvard Graduate', 'I': ''}, 'Detroit': {'Acy': 'Automobile Country', 'At': 'Detroit Athletic', 'Au': 'Automobile of Detroit', 'Bh': 'Bloomfield Hills Country', "Cal'": 'California Univ Graduate', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', "Cl'": 'Columbia Graduate', 'Cl': 'College', "Cr'": 'Cornell Graduate', 'Cw': 'Society of Colonial Wars', 'Cy': 'Country', 'D': 'Detroit', 'Dar': 'Daughters of American Revolution', 'Daughters': 'of American Revolution', 'Db': 'Detroit Boat', 'Dg': 'Detroit Golf', 'Fl': 'Fellowcraft Athletic', 'G': 'Garden', 'Gi': 'Grosse He Country', "H'": 'Harvard Graduate', 'Hu': 'Grosse Pointe Riding & Hunt', 'Ig': 'Ingleside', "Mich'": 'Michigan Graduate', 'Mv': 'Mt Vernon Society', 'Myf': 'Mayflower Descendants', "P'": 'Princeton Graduate', "Pa'": 'Univ of Pa Graduate', 'Tc': 'Twentieth Century', 'Uv': 'University', "Wms'": "Williams' Graduate", 'Wo': 'Wolverine Automobile', "Y'": 'Yale Graduate', 'Yo': 'Yondotega', "USA'": 'I', "USN'": 'I of West Point Annapolis', 'CT': 'Columbia Graduate'}, 'Los Angeles': {'An': 'Annandale Golf', 'Be': 'Bolsa Chica Gun', "Cal'": 'Univ of California Graduate', 'Cd': 'Colonial Darnes', 'Cer': 'Cerritos Gun', 'Clf': 'California', 'Crc': 'Crags Country', 'Cw': 'Society of Colonial Wars', 'Cy': 'Los Angeles Country', "H'": 'Harvard Univ Graduate', 'Jno': 'Jonathan', 'Mid': 'Midwick Country', "P'": 'Princeton Univ Graduate', 'Sgc': 'San Gabriel Country', "Stan'": 'Stanford Univ Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'Uv': 'University', 'Vh': 'Valley Hunt', "Y'": 'Yale Univ Graduate', 'CI': 'California', 'Rv': 'Sons of the Revolution', 'Sgs': 'San Gabriel Country'}, 'Minneapolis': {'Ar': 'Sons of American Revolution', 'Au': 'Automobile', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', "Cr'": 'Cornell University Graduate', 'Cw': 'Society of Colonial Wars', 'Dar': 'Daughters of American Revolution', "Dth'": 'Dartmouth College Graduate', "H'": 'Harvard University Graduate', 'LI': 'Loyal Legion', 'Mk': 'Minikahda', 'Mnp': 'Minneapolis', 'Mns': 'Minnesota', "P'": 'Princeton University Graduate', 'Rv': 'Sons of Revolution', 'Tc': 'Town & Country', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'Wby': 'White Bear Yacht', 'Wt': 'Society of War of Bia', "Y'": 'Yale University Graduate', "Gene'ated": 'Harvard University 2021 12 17 14 31 GMT 2027 89081191462', 'Uv': 'University'}, 'New Orleans': {'Ag': 'Audobon Golf', 'Bos': 'Boston Club', 'Ccw': 'Chess Checkers Whist', 'Crn': 'Carnival German', 'Cy': 'New Orleans Country', 'Fo': 'French Opera', "H'": 'Harvard Graduate', 'La': 'Louisiana', 'Mdc': 'Midwinter Cotillion', 'Pic': 'Pickwick', 'Rt': 'Round Table', 'St': 'Stratford', 'Sy': 'Southern Yacht', "Tul'": 'Tulane Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', "Y'": 'Yale Graduate'}, 'Pittsburgh': {'Ac': 'Allegheny Country', "Br'": 'Brown Univ Graduate', 'Cy': 'Country', 'Dq': 'Duquesne', "Dth'": 'Dartmouth Graduate', 'Edg': 'Edgeworth Country', "H'": 'Harvard Graduate', 'F': 'Princeton Graduate', 'P': 'Pittsburgh', "Pa'": 'Univ of Penn Graduate', 'Pg': 'Pittsburgh Golf', 'Un': 'Union', 'Uv': 'University', "Y'": 'Yale Graduate', "P'": 'Princeton Graduate', 'H': 'Harvard Graduata', 'Pa': 'Univ of Penn Graduate', 'Y': 'Yale Graduate', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', 'Dar': 'Daughters of American Revolution', 'Br': 'Brown University Graduate', 'Dtn': 'Dartmouth Graduate', "Cr'": 'Cornell Graduate', 'Cr': 'Cornell Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'At': 'Pittsburgh Athletic', 'Pr': 'Princeton Graduate', 'USM': 'Marine Corps'}, 'Providence': {'A': 'Art', 'Aga': 'Agawam Hunt', 'Au': 'R I Automobile', "Br'": 'Brown Univ Graduate', "H'": 'Harvard Univ Graduate', 'Hp': 'Hope', 'J': "Hop' Johns Hopkins Graduate", 'Mtg': 'Metacomet Golf', 'Pu': 'Psi Upsilon', 'Rmp': 'Rumford Polo', 'Ry': 'R I Yacht', 'Sq': 'Squantum', 'Uv': 'University', 'Wng': 'Wannamoisett Country', "Aht'": 'Amherst Graduate', "P'": 'Princeton Univ Graduate', "Pa'": 'Univ of Penn Graduate', 'Y': 'Yale Univ Graduate', 'Br': 'Brown Univ Graduate', 'Pa': 'Univ of Penn Graduate', "Cr'": 'Cornell Univ Graduate', "Y'": 'Yale Univ Graduate', 'Ar': 'Sons of American Revolution', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', 'Rv': 'Sons of Revolution', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'Wnc': 'Wannamoisett Country'}, 'Seattle': {"Cal'": 'Univ of California Graduate', "Cr'": 'Cornell University Graduate', 'Cy': 'Country of Bainbridge Island', "H'": 'Harvard Graduate', "P'": 'Princeton Graduate', 'Ra': 'Rainier', 'Sg': 'Seattle Golf', "Stan'": 'Stanford Univ Graduate', "USA'": 'Graduate of West Point', "USN'": 'Graduate of Annapolis', 'Uv': 'University', 'Y': 'Yale Graduate', 'Cl': 'College', "Y'": 'Yale Graduate', "CbI'": 'Univ of California Graduate'}, 'St Louis': {'Cm': 'Commercial', 'Cw': 'Colonial Wars', 'Cy': 'St Louis Country', 'Dar': 'Daughters of American Revolution', 'Me': 'Mercantile', 'Nd': 'Noonday', 'Rt': 'Round Table', 'Rv': 'Sons of Revolution', 'SI': 'St Louis', 'Uv': 'University', 'Wd': 'Wednesday', "Br'": 'Brown Univ Graduate', 'Cd': 'Colonial Dames', 'Cda': 'Colonial Dames of America', "Cr'": 'Cornell Graduate', "H'": 'Harvard Graduate', "Pa'": 'Univ of Penn Graduate', 'Wn': "Woman's", 'Wt': 'War of 1812', "Y'": 'Yale Graduate', 'Br': 'Brown Univ Graduate', 'Louis': 'Country', 'Ar': 'Sons of American Revolution', 'Myf': 'Society of Mayflower Descendants', 'Rc': 'Racquet Club', 'Bv': 'Bellerive Country', 'Lc': 'Log Cabin'}}


# In[6]:


# Clean the blank lines
def clean_blank(lines:list):
    output = []
    # Delete the blank lines, and the blank 
    for line in lines:
        if line != "\n" and line != "+\n":
            output.append(line)
    for i in range(len(output)):
        if re.search("\n", output[i]) is not None:
                output[i] = re.sub("\n", ' ', output[i])
    return output

# Concoct the broken lines for multiple  lines of name-address
def clean_bracket(outputleft:list):
    #print(outputleft,len(outputleft))

    if len(outputleft) != 0:
        i = 0
        while i < len(outputleft) - 1:
            if re.search("\[(.*)", outputleft[i]) is None and re.search("\[(.*)", outputleft[i + 1]) is not None:
                bracket = re.search("\[(.*)", outputleft[i + 1]).group(1)
                bracket = re.sub("\(", "\\(", bracket)
                bracket = re.sub("\)", "\\)", bracket)
                bracket = re.sub("\[", "\\[", bracket)
                outputleft[i] = outputleft[i] + ' ' + bracket
                try:
                    outputleft[i + 1] = re.sub(bracket, "", outputleft[i + 1])
                except:
                    print(bracket)
            i += 1

    if len(outputleft)!= 0 :
        i = 0
        while i < len(outputleft):
            if i+1 < len(outputleft) and re.search(TITLE_PATTERNS,outputleft[i]) is not None and re.search("\(",outputleft[i]) is not None and re.search("\)",outputleft[i]) is None and  re.search("\(",outputleft[i+1]) is None and re.search("\)",outputleft[i+1]) is not None:
                outputleft[i] = outputleft[i] + ' ' + outputleft[i+1]
                outputleft.pop(i+1)
            elif i+2 < len(outputleft)and re.search(TITLE_PATTERNS,outputleft[i]) is not None and re.search("\(",outputleft[i]) is not None and re.search("\)",outputleft[i]) is None and  re.search("\(",outputleft[i+2]) is None and re.search("\)",outputleft[i+2]) is not None:
                outputleft[i] = outputleft[i] + ' ' + outputleft[i+2]
                outputleft.pop(i+2)
            else:
                i += 1

    #print(outputleft, len(outputleft))
    return outputleft

def general_cleaner(input: list):
    output = []
    for line in range(len(input)):
        input[line] = input[line].strip()
        if "Public Domain, Google-digitized" in input[line] or "Generated at Harvard University" in input[line] \
                or 'Digitized' in input[line]:
            input[line] = ''
        if "â€™" in input[line]:
            input[line] = input[line].replace("â€™", "'")
        if "\\" in input[line]:
            input[line] = input[line].replace("\\", "")
        if "Ã©" in input[line]:
            input[line] = input[line].replace("Ã©", "é")


        #SPACING
        if re.search(r"^[A-Z][a-z][A-Z][a-z]", input[line]) is None:
            try:
                input[line]=re.sub(r"(^[A-Z][a-z]+(?![ a-z]))", r"\1 ", input[line])
            except:
                pass
        else:
            try:
                input[line]=re.sub(r"(^[A-Z][a-z][a-z]?[A-Z][a-z]+(?![ a-z]))", r"\1 ", input[line])
            except:
                pass
        try:
            input[line]=re.sub(r"((?<=\S)(?<!\()(?<![A-Z][a-qs-z])(?<![A-Z][a-z][a-z])(?<!\&)[A-Z][a-z]+)", r" \1", input[line])
        except:
            pass

    for line in range(len(input)):
        try:
            linecheck=input[line+1]
            if input[line][-1]=="-" and re.search(r"^[a-z]", input[line+1]) is not None:
                input[line]=re.sub(r"(\-$)", "", input[line]) + input[line+1]
                input[line+1]=""
        except:
            pass

    for k in range(len(input)):
        if re.search(PARENTHESES_BEFORE_STRING,input[k]) is not None:
            input[k] = re.sub(r"\)", r") ", input[k])
        if re.search(PARENTHESES_AFTER_STRING,input[k]) is not None:
            input[k] = re.sub(r"\(", r" (", input[k])
        if re.search(SPACING_OF_HYPHENS,input[k]) is not None:
            input[k] = re.sub(r"\-", r" \- ", input[k])
        if re.search (TITLE_FIX_END_OF_PREV, input[k]) is not None:
            match_part = re.search(TITLE_FIX_END_OF_PREV, input[k]).group(1)
            input[k] = re.sub(f"{match_part}", f"{match_part} ",input[k])

        input[k] = re.sub(r"([a-z]{1,})(?! )([A-Z])", r"\1 \2", input[k])
        input[k] = re.sub('([A-Z]")(?! )([A-Z][a-z])', r"\1 \2",input[k])
        input[k] = re.sub("([A-Z]')(?! )([A-Z][a-z])", r"\1 \2", input[k])
        words = input[k].split(" ")
        output.append(" ".join(words))

    return output



def add_spaces(to_be_cleaned: str, type: str):
    # add space between two upper case letter in the same string
    _ = re.sub("([A-Z])([A-Z][a-z]{1,})", r"\1 \2", to_be_cleaned)
    # add space between a lower case letter and upper case letter in the same string
    __ = re.sub(r"\b([A-z]?[a-z]{1,})([A-Z][^a-z])", r"\1 \2", _)
    # split the words into a list by spaces
    output = __.split(" ")
    # Adjust the wrong title
    for i in range(len(output)):
        for key in NAME_ABBRV:
            if output[i] == key:
                output[i] = NAME_ABBRV[key]
    # Adjust to full name       
    for i in range(len(output)):
        for key in CORRECT_TITLES:
            for WRONG_TITLE in CORRECT_TITLES [key]:
                if output[i] == WRONG_TITLE:
                    output[i] = key
       
    if type == "STRING":
        return " ".join(output)
    elif type == "LIST":
        return list(output)
    
def add_space_junior(to_be_cleaned: str):
    # add space between two upper case letter in the same string
    _ = re.sub("([A-Z])([A-Z][a-z]{1,})", r"\1 \2", to_be_cleaned)
    # add space between a lower case letter and upper case letter in the same string
    __ = re.sub(r"\b([A-z]?[a-z]{1,})([A-Z][^a-z])", r"\1 \2", _)
    # add space between a letter and non-letter characteristic
    ___ = re.sub(r"([A-Z][a-z]*)(?! )(&)", r"\1 \2", __)
    output = ___.split(" ")
    
    return " ".join(output)
    

#Generate the address
def clean_address(outputright: list):
    #print(outputright)
    address = ""
    for i in range(len(outputright)):
        if re.search(PHONE,outputright[i]) is None and re.search(OTHER,outputright[i]) is None and re.search(PHONE2,outputright[i]) is None and re.search(PHONE3,outputright[i]) is None and re.search(PHONE4,outputright[i]) is None:
            address = address + outputright[i]
        else:
            pass
    #print(address)

    for key in CORRECT_ADDRESS:
        for WRONG_ADDRESS in CORRECT_ADDRESS [key]:
            if re.search(WRONG_ADDRESS,address) is not None:
                address = re.sub(WRONG_ADDRESS,key, address)

    address = re.sub(TRIVIAL, '', address)
    address = re.sub(ELSE, '', address)
    address = re.sub(TIME, '', address)
    address = re.sub("([A-Z])([A-Z])", r"\1 \2", address)
    address = re.sub("([A-z]?[a-z]{1,})([A-Z])", r"\1 \2", address)
    address = re.sub(r"([A-Za-z]+)([0-9]+)", r"\1 \2", address)
    address = re.sub(r"([0-9]+)([A-Za-z]+)", r"\1 \2", address)
    #print(address)
    address = re.sub(OTHER2, '', address)
    #print(address)

    if address.isspace():
        address = ""
    return address
    

#Create the result for multiple lines of family
def generate_result(outputleft:list, outputright:list):
    
    global household
    global marriage
    household_last_name = None

    #left = outputleft[:]
    #r1 = [left,len(left)]
    #Clean the lines
    if len(outputleft) != 0 and len(outputright) != 0:
        k = 0
        while k < len(outputleft)-1:
            if re.search(EXTREME_TITLE_DETECTION, outputleft[k+1]) is None and re.search(OTHER_DETECTION, add_space_junior(outputleft[k+1])) is None and re.search(JUNIOR_DETECTION,add_space_junior(outputleft[k+1])) is None and re.search("\\.",outputleft[k+1]) is not None:
                outputleft[k] = outputleft[k] + ' ' + outputleft[k + 1]
                outputleft.pop(k+1)
            else:
                k += 1

        k = 0
        while k < len(outputleft):
            if re.search(EXTREME_TITLE_DETECTION,outputleft[k]) is None and re.search(OTHER_DETECTION, add_space_junior(outputleft[k])) is None and re.search(JUNIOR_DETECTION,add_space_junior(outputleft[k])) is None:
                outputleft.pop(k)
            else:
                k += 1
        #print("B", len(outputleft), outputleft)
        if len(outputleft) > 0 and re.search(JUNIOR_DETECTION, add_space_junior(outputleft[0])) is not None:
            outputleft.clear()
        if len(outputleft) > 0 and re.search(EXTREME_TITLE_DETECTION,outputleft[0]) is None and re.search(OTHER_DETECTION, add_space_junior(outputleft[0])) is not None:
            outputleft.clear()
        #r2 = [outputleft,len(outputleft)]
        #if r1[1] != r2[1]:
        #    print(r1,r2)
        #print("D",len(outputleft),outputleft)

    if len(outputleft) != 0 and len(outputright) != 0:
        #print(len(outputleft),outputleft)
        # Update household ID
        #if len(outputleft) > 1:
        #    household += 1
        #elif len(outputleft) == 1 and re.search("\(.+\)", outputleft[0]) is not None:
        household += 1
            
        for k in range(len(outputleft)):

            if marriage == 1:
                break
            for line in outputleft:
                if "MARRIAGES OF" in line or "Marriages OF" in line or "Marriages Of" in line or "Marriages of" in line:
                    marriage = 1
                    break
            for line in outputright:
                if "MARRIAGES OF" in line or "Marriages OF" in line or "Marriages Of" in line or "Marriages of" in line:
                    marriage = 1
                    break

            # print(outputleft[k])
            junior_name = re.search(JUNIOR_DETECTION, add_space_junior(outputleft[k]))
            # print(re.findall(JUNIOR_DETECTION,add_space_junior(outputleft[k])))
            full_name = re.search(EXTREME_TITLE_DETECTION, outputleft[k])
            fullname = re.findall(EXTREME_TITLE_DETECTION, outputleft[k])
            # print(fullname)
            other_name = re.search(OTHER_DETECTION,  add_space_junior(outputleft[k]))
            # print(full_name,junior_name,other_name)


            #try:
            #    line_for_information = outputleft[k] + re.search("(\[)(.*)",outputleft[k + 1]).group(2)
            #except:
            #    line_for_information = outputleft[k]


            die = 0
            try:
                re.search(DEATHECTION, outputleft[k]).group(9)
                die = 1
            except:
                pass
            died.append(die)
            #print(die)
            #print(len(died))

            clubs = []
            gradyear = ''
            college_complete = ''
            clubs_complete = []
            cityclubs = CITY_CLUBS[city]
            keys = list(cityclubs)
            for j in keys:
                if "," in j:
                    j = j.replace(",", ".")
                # club_full = re.findall(r"" + j + "(?=\.)|" + j + "(?=[0-9o][0-9o])|(?<=" + j + ")[0-9o][0-9o]", line)
                club_full = re.findall(r"" + j + "(?=\.)|" + j + "[0-9o][0-9o]", outputleft[k])
                if len(club_full) > 0:
                    clubs.append(club_full[0])
                    if re.search(r"" + j + "[0-9o][0-9o]", outputleft[k]) is not None:
                        uni = re.search(r"(" + j + "(?=[0-9o][0-9o]))", outputleft[k]).group(1)
                        if "'" not in uni:
                            uni = uni + "'"
                        grad_year_base = re.search(r"((?<=" + j + ")[0-9o][0-9o])", outputleft[k]).group(1)
                        if "o" in grad_year_base:
                            grad_year_base = grad_year_base.replace("o", "0")
                        if 1900 + int(grad_year_base) > int(year):
                            gradyear = str(1800 + int(grad_year_base))
                        else:
                            gradyear = str(1900 + int(grad_year_base))

                        try:
                            univer = CITY_CLUBS[city][uni]
                            college_complete = str(univer + ' ' + gradyear)
                        except:
                            pass
                    else:
                        try:
                            clubs_complete.append(CITY_CLUBS[city][j])
                        except:
                            pass

            if len(clubs) > 0:
                clubs_raw.append(', '.join(clubs))
            else:
                clubs_raw.append('')
            if len(clubs_complete) > 0:
                clubs_clean.append(', '.join(clubs_complete))
            else:
                clubs_clean.append('')
            grad_year.append(gradyear)
            college.append(college_complete)
            #print(clubs, clubs_complete, gradyear)
            #print(len(clubs_raw))

            
            col_city.append(city)
            col_year.append(year)
            addr_origin = clean_address(outputright)
            if re.search(MOVE, addr_origin) is not None:
                addr = re.sub(MOVE,'',addr_origin)
                move = re.search(MOVE, addr_origin).group(2)
                col_address.append(addr)
                newregister.append(move)
            else:
                col_address.append(addr_origin)
                newregister.append('')

            try:
                foreign.append(re.search(FOREIGN, outputright).group(0))
            except:
                foreign.append("No")
            #print(outputright)
            #print(clean_address(outputright))
            #print(col_city,col_year,col_address)
            #print(len(col_city),len(col_year),len(col_address))

            col_household.append(household)
            #print(col_household)
            #print(len(col_household))

            if k == 0 and len(outputleft) > 1:
                col_hhhead.append('1')
                if re.search(EXTREME_TITLE_DETECTION,outputleft[k]) is not None:
                    household_last_name = full_name.group(1)
            elif k == 0 and re.search("\(.+\)",outputleft[0]) is not None and len(outputleft) == 1:
                col_hhhead.append('1')
            elif k == 0 and re.search("\(.+\)",outputleft[0]) is None and len(outputleft) == 1:
                col_hhhead.append('0')
            elif k > 0 and full_name is None and other_name is not None:
                col_hhhead.append('5')
            elif k > 0 and junior_name is not None:
                col_hhhead.append('3')
            else:
                col_hhhead.append('4')
            #print(col_hhhead)
            #print(len(col_hhhead))
                
            #if re.search(BRACKET,outputleft[k]) is not None:
            #    col_bracket.append('1')
            #else:
            #    col_bracket.append('0')
            #print(col_bracket)
            #print(len(col_bracket))
    
            if junior_name is not None:
                #print(k,"case1", junior_name)
                junior_number = outputleft[k].count('&')+1
                if len(outputleft) > 1 and k == len(outputleft)-1:
                    for i in range(junior_number):
                        if 4*(i+1)+1 < len(junior_name.groups()) and junior_name.group(4*(i+1)+1) is not None:
                            if i == 0:
                                if household_last_name is not None:
                                    col_lastname.append(household_last_name)
                                else:
                                    col_lastname.append('Junior')
                                col_spousename.append('None')
                                col_spouselast.append('None')
                                col_spousemiddle.append('')
                            elif i > 0:
                                col_household.append(col_household[-1])
                                col_hhhead.append(col_hhhead[-1])
                                col_city.append(col_city[-1])
                                col_year.append(col_year[-1])
                                col_address.append(col_address[-1])
                                newregister.append(newregister[-1])
                                col_lastname.append(household_last_name)
                                col_spousename.append('None')
                                col_spouselast.append('None')
                                col_spousemiddle.append('')
                                foreign.append(foreign[-1])
                                died.append('0')
                                clubs_raw.append('')
                                clubs_clean.append('')
                                grad_year.append('')
                                college.append('')

                            if junior_name.group(4*(i+1)) is not None:
                                col_title.append(add_spaces(junior_name.group(4*(i+1)),"STRING"))
                            elif i == 0 and junior_name.group(4*(i+1)) is None:
                                col_title.append('')
                            elif i > 0 and  4*(i+1) < len(junior_name.groups()) and junior_name.group(4*(i+1)) is None and junior_name.group(4*i) is not None:
                                col_title.append(add_spaces(junior_name.group(4*i),"STRING"))
                            elif i > 0 and  4*(i+1) < len(junior_name.groups()) and junior_name.group(4*(i+1)) is None and junior_name.group(4*i) is None:
                                 col_title.append('')

                            first_and_middle_name = add_spaces(junior_name.group(4*(i+1)+1),"LIST")
                            if len (first_and_middle_name) == 1:
                                col_middlename.append(' ')
                                col_firstname.append(first_and_middle_name[0]) 
                            elif len (first_and_middle_name) > 1:
                                col_firstname.append(first_and_middle_name[0])
                                col_middlename.append(' '.join(first_and_middle_name[1:]))
                                if len(first_and_middle_name[0]) == 1:
                                    for m in range(len(first_and_middle_name[1:])):
                                        if len(first_and_middle_name[m]) > 1:
                                            col_firstname.pop()
                                            col_firstname.append(first_and_middle_name[m])
                                            col_middlename.pop()
                                            col_middlename.append(' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:]))
                                            break

                else:
                   #print(k,'case2',junior_name)
                    for i in range(junior_number):
                        if 4*(i+1)+1 < len(junior_name.groups()) and junior_name.group(4*(i+1)+1) is not None:
                            if i == 0:
                                if household_last_name is not None:
                                    col_lastname.append(household_last_name)
                                else:
                                    col_lastname.append('Junior')
                                col_spousename.append('None')
                                col_spouselast.append('None')
                                col_spousemiddle.append('')
                            elif i > 0:
                                col_household.append(col_household[-1])
                                col_hhhead.append(col_hhhead[-1])
                                col_city.append(col_city[-1])
                                col_year.append(col_year[-1])
                                col_address.append(col_address[-1])
                                newregister.append(newregister[-1])
                                col_lastname.append('Junior')
                                col_spousename.append('None')
                                col_spouselast.append('None')
                                col_spousemiddle.append('')
                                foreign.append(foreign[-1])
                                died.append('0')
                                clubs_raw.append('')
                                clubs_clean.append('')
                                grad_year.append('')
                                college.append('')

                            if junior_name.group(4*(i+1)) is not None:
                                col_title.append(add_spaces(junior_name.group(4*(i+1)),"STRING"))
                            elif i == 0 and junior_name.group(4*(i+1)) is None:
                                col_title.append('')
                            elif i > 0 and  4*(i+1) < len(junior_name.groups()) and junior_name.group(4*(i+1)) is None and junior_name.group(4*i) is not None:
                                col_title.append(add_spaces(junior_name.group(4*i),"STRING"))
                            elif i > 0 and  4*(i+1) < len(junior_name.groups()) and junior_name.group(4*(i+1)) is None and junior_name.group(4*i) is None:
                                 col_title.append('')

                            first_and_middle_name = add_spaces(junior_name.group(4*(i+1)+1),"LIST")
                            if len (first_and_middle_name) == 1:
                                col_middlename.append(' ')
                                col_firstname.append(first_and_middle_name[0]) 
                            elif len (first_and_middle_name) > 1:
                                col_firstname.append(first_and_middle_name[0])
                                col_middlename.append(' '.join(first_and_middle_name[1:]))
                                if len(first_and_middle_name[0]) == 1:
                                    for m in range(len(first_and_middle_name[1:])):
                                        if len(first_and_middle_name[m]) > 1:
                                            col_firstname.pop()
                                            col_firstname.append(first_and_middle_name[m])
                                            col_middlename.pop()
                                            col_middlename.append(' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:]))
                                            break
                     
            elif junior_name is None:
                
                if full_name is not None:
                    #print(k,'case3',full_name)
                    #fullname = re.findall(EXTREME_TITLE_DETECTION,outputleft[k])
                    #print(fullname)
                    col_lastname.append(add_spaces(full_name.group(1),"STRING"))
                    col_title.append(add_spaces(full_name.group(2),"STRING"))
                    first_and_middle_name = add_spaces(full_name.group(3),"LIST")
                    if len (first_and_middle_name) == 1:
                        col_middlename.append(' ')
                        col_firstname.append(first_and_middle_name[0]) 
                    elif len (first_and_middle_name) > 1:
                        col_firstname.append(first_and_middle_name[0])
                        col_middlename.append(' '.join(first_and_middle_name[1:]))
                        if len(first_and_middle_name[0]) == 1:
                            for m in range(len(first_and_middle_name[1:])):
                                if len(first_and_middle_name[m]) > 1:
                                    col_firstname.pop()
                                    col_firstname.append(first_and_middle_name[m])
                                    col_middlename.pop()
                                    col_middlename.append(' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:]))
                                    break

                    if full_name.group(7) is not None:
                        spouse_name = add_spaces(full_name.group(7),"LIST")
                        if len(spouse_name) == 1:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[0])
                            col_spousemiddle.append('')
                        elif len(spouse_name) == 2:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[1])
                            col_spousemiddle.append('')
                        elif len(spouse_name) > 2:
                            col_spousename.append(spouse_name[0])
                            col_spousemiddle.append(' '.join(spouse_name[1:-1]))
                            col_spouselast.append(spouse_name[-1])   
                    else:
                        col_spousename.append('None')
                        col_spouselast.append('None')
                        col_spousemiddle.append('')
                        
                elif other_name is not None:
                    othername = re.findall(OTHER_DETECTION,add_space_junior(outputleft[k]))
                    #print(k,'case4', othername)
                    if household_last_name is not None:
                        col_lastname.append(household_last_name)
                    else:
                        col_lastname.append('Other')
                    col_title.append(add_spaces(other_name.group(2),"STRING"))
                    first_and_middle_name = add_spaces(other_name.group(3),"LIST")
                    if len (first_and_middle_name) == 1:
                        col_middlename.append(' ')
                        col_firstname.append(first_and_middle_name[0]) 
                    elif len (first_and_middle_name) > 1:
                        col_firstname.append(first_and_middle_name[0])
                        col_middlename.append(' '.join(first_and_middle_name[1:]))
                        if len(first_and_middle_name[0]) == 1:
                            for m in range(len(first_and_middle_name[1:])):
                                if len(first_and_middle_name[m]) > 1:
                                    col_firstname.pop()
                                    col_firstname.append(first_and_middle_name[m])
                                    col_middlename.pop()
                                    col_middlename.append(' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:]))
                                    break

                    if other_name.group(7) is not None:
                        spouse_name = add_spaces(other_name.group(7),"LIST")
                        if len(spouse_name) ==1:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[0])
                            col_spousemiddle.append('')
                        elif len(spouse_name) == 2:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[1])
                            col_spousemiddle.append('')
                        elif len(spouse_name) > 2:
                            col_spousename.append(spouse_name[0])
                            col_spousemiddle.append(' '.join(spouse_name[1:-1]))
                            col_spouselast.append(spouse_name[-1])   
                    else:
                        col_spousename.append('None')
                        col_spouselast.append('None')
                        col_spousemiddle.append('')
                    

    #print(len(col_bracket), len(col_city), len(col_year), len(col_household), len(col_hhhead), len(col_lastname), len(col_title), len(col_middlename), len(col_firstname), len(col_spousename), len(col_spouselast), len(col_spousemiddle), len(col_address))

    if any(len(lst) != len(col_city) for lst in [newregister,col_city,col_year,col_lastname,col_title,col_middlename,col_firstname,col_spousename,col_spousemiddle,col_spouselast,col_address,col_household,col_hhhead,clubs_raw,clubs_clean,grad_year,foreign,died]):
        print("city:", col_city, "year:", col_year, "household_id:", col_household,
             "household_structure:", col_hhhead,
              "last_name:", col_lastname, "title:", col_title, "first_name:", col_firstname,
              "middle_names:", col_middlename,
             "spouse_name:", col_spousename, "spouse_middle_names:", col_spousemiddle, "spouse_last_name:", col_spouselast,
              "clubs_abbr:", clubs_raw, "clubs_extended:", clubs_clean, "grad_year:", grad_year,
              "foreign:", foreign, "died:", died, "address:", col_address,"new_register:", newregister)
        print ("city:", len(col_city), "year:", len(col_year), "household_id:", len(col_household), "household_structure:", len(col_hhhead),
                "last_name:", len(col_lastname), "title:", len(col_title), "first_name:", len(col_firstname), "middle_names:", len(col_middlename),
                "spouse_name:", len(col_spousename), "spouse_middle_names:", len(col_spousemiddle), "spouse_last_name:", len(col_spouselast),
                 "clubs_abbr:", len(clubs_raw), "clubs_extended:", len(clubs_clean), "grad_year:", len(grad_year), "foreign:", len(foreign),
                 "died:", len(died), "address:", len(col_address),"new_register:", len(newregister))

    return newregister, household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address
    
                


# In[7]:


def match_family(left:str,right:str):
    
    lefttxt = open(left, 'r', encoding="UTF-8")
    righttxt = open(right, 'r', encoding="UTF-8")
    leftlines = lefttxt.readlines()
    rightlines = righttxt.readlines()

    #print("A", len(leftlines), leftlines)
    outputleft = clean_blank(leftlines)
    outputright = clean_blank(rightlines)
    outputleft = general_cleaner(outputleft)
    outputright = general_cleaner(outputright)
    #print("B", len(outputleft), outputleft)
    outputleft = clean_bracket(outputleft)
    #print("C", len(outputleft), outputleft)
    newregister, household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address = generate_result(outputleft,outputright)
    


# In[8]:


class Logger(object):
    def __init__(self, filename="Default.log", encoding="utf-8"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding=encoding)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

sys.stdout = Logger('compare.txt', encoding='utf-8')


##Set the  path of the input txts of the family (left:name,right:address)
workdir = "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\"
csvpath = workdir+"csv_output_original\\"
if os.path.exists(csvpath):
    shutil.rmtree(csvpath)
os.makedirs(csvpath)

household_dic = {}

for txtpath,txtdirs,_ in os.walk(workdir+"text_output_household"):
    for txtdir in txtdirs:
        city = re.findall(r"[A-z ]+(?= [0-9])", txtdir)[0]
        year = re.findall(r"[0-9]+", txtdir)[0] 
        
        col_city = []
        col_year = []
        col_lastname = []
        col_title = []
        col_middlename = []
        col_firstname = []
        col_spousename = []
        col_spousemiddle = []
        col_spouselast = []
        col_address = []
        col_household = []
        col_hhhead = []
        clubs_raw = []
        clubs_clean = []
        college = []
        grad_year = []
        foreign = []
        died = []
        newregister = []
        household = 0
        marriage = 0

        for i in range(1,500000):
            left_txt = os.path.join(txtpath,city+' '+year,"L"+str(i).zfill(5)+".txt")
            right_txt = os.path.join(txtpath,city+' '+year,"R"+str(i).zfill(5)+".txt")
            if os.path.exists(left_txt) and os.path.exists(right_txt):
                match_family(left_txt, right_txt)
                
        #print(len(col_household))
        #print(col_household)
        household_dic[city+year] = col_household[-1]
        data = pd.DataFrame(
            {"city": col_city, "year": col_year, "household_id": col_household, "household_structure": col_hhhead,
             "last_name": col_lastname, "title": col_title, "first_name": col_firstname, "middle_names": col_middlename,
             "spouse_name": col_spousename, "spouse_middle_names": col_spousemiddle, "spouse_last_name": col_spouselast,
             "clubs_abbr": clubs_raw, "clubs_extended": clubs_clean,"college":college, "grad_year": grad_year, "foreign": foreign,
             "died": died, "address": col_address, "new_register":newregister})
        csvfile = csvpath+city+' '+year+".csv"
        if os.path.exists(csvfile):
            os.remove(csvfile)
        data.to_csv(csvfile,index=0)   



# In[16]:



#Concoct the broken lines for single line of name-address
def clean_line_single(inputlines:list):
    #input1 = inputlines
    #r1 = [input1,len(input1)]
    i = 0
    while i < len(inputlines) - 1:
        if re.search("\[(.*)", inputlines[i]) is None and re.search("\[(.*)", inputlines[i + 1]) is not None:
            bracket = re.search("\[(.*)", inputlines[i + 1]).group(1)
            #print(bracket)
            bracket = re.sub("\(", "\\(", bracket)
            bracket = re.sub("\)", "\\)", bracket)
            bracket = re.sub("\[", " ",  bracket)
            inputlines[i] = inputlines[i] + ' ' + bracket
            try:
                inputlines[i + 1] = re.sub(bracket, "", inputlines[i + 1])
            except:
                pass
                #print("else",bracket)
        i += 1
    #print(inputlines, len(inputlines))

    i = 0
    while i < len(inputlines):
        #print("A1",inputlines[i])

        #elif i+3 < len(inputlines)and re.search(LINE_AFTER_PREV,inputlines[i+1]) is not None and re.search(LINE_AFTER_PREV,inputlines[i+2]) is not None:
            #inputlines[i+1] = inputlines[i+1] + '' + inputlines[i+2]
            #inputlines.pop(i+2)
        if i+3 < len(inputlines) and re.search(EXTREME_TITLE_DETECTION, inputlines[i]) is not None and re.search(EXTREME_TITLE_DETECTION, inputlines[i+1]) is not None and re.search(LINE_AFTER_PREV,inputlines[i+1]) is None and re.search(LINE_AFTER_PREV,inputlines[i+2]) is not None and re.search(LINE_AFTER_PREV,inputlines[i+3]) is not None:
            inputlines[i] = inputlines[i] + ' ' + inputlines[i+2]
            inputlines.pop(i+2)
            #print("A2", inputlines[i])
        elif i+1 < len(inputlines) and re.search(EXTREME_TITLE_DETECTION, inputlines[i]) is not None and re.search(EXTREME_TITLE_DETECTION, inputlines[i+1]) is None and re.search(LINE_AFTER_PREV, inputlines[i + 1]) is not None:
            inputlines[i] = inputlines[i] + ' ' + inputlines[i + 1]
            inputlines.pop(i + 1)
            #print("A3", inputlines[i])
        elif i+1 < len(inputlines) and re.search(EXTREME_TITLE_DETECTION, inputlines[i]) is not None and re.search(NAME_ADDRESS_DETECTION,inputlines[i]) is None and re.search(NAME_ADDRESS_DETECTION_EXACT,inputlines[i]) is None and re.search(EXTREME_TITLE_DETECTION,inputlines[i+1]) is None:
            inputlines[i] = inputlines[i] + ' ' + inputlines[i+1]
            inputlines.pop(i+1)
            #print("A4", inputlines[i])
        else:
            #print("A5", inputlines[i])
            i += 1

    #print(inputlines,len(inputlines))
    
    #for line in inputlines:
    #    line = re.sub("\. \.","\.\.",line)
        
    return inputlines
   
def clean_address_single(address:list):
    for key in CORRECT_ADDRESS:
        for WRONG_ADDRESS in CORRECT_ADDRESS[key]:
            if re.search(WRONG_ADDRESS, address) is not None:
                address = re.sub(WRONG_ADDRESS, key, address)
    
    address = re.sub(TRIVIAL, '', address)
    address = re.sub(OTHER, '', address)
    address = re.sub(ELSE, '', address)
    address = re.sub(TIME, '', address)
    address = re.sub(PHONE,'',address)
    address = re.sub("([A-Z])([A-Z])", r"\1 \2", address)
    address = re.sub("([A-z]?[a-z]{1,})([A-Z])", r"\1 \2", address)
    address = re.sub(r"([A-Za-z]+)([0-9]+)", r"\1 \2", address)
    address = re.sub(r"([0-9]+)([A-Za-z]+)", r"\1 \2", address)
    address = re.sub('^\s+', '', address)
    address = re.sub(OTHER2, '', address)
                    
    if re.search(ELSE, address) is not None or re.search(OTHER, address) is not None:
        address=""
    elif address.isspace():
        address = ""

    return address

#Create the result for a single line of  household
def generate_result_single(inputlines: list):
    
    global household
    global marriage

    if len(inputlines) != 0 :
        k = 0
        while k < len(inputlines):
            if marriage == 1:
                break
            if "MARRIAGES OF" in inputlines[k] or "Marriages OF" in inputlines[k] or "Marriages Of" in inputlines[k] or "Marriages of" in inputlines[k]:
                marriage = 1
                break
            # print(inputlines[k])
            name_and_address = None
            full_name = None
            spouse_full_name = None

            full_name = re.search(EXTREME_TITLE_DETECTION, inputlines[k])
            if k < len(inputlines) -1:
                spouse_full_name = re.search(EXTREME_TITLE_DETECTION, inputlines[k+1])

            #if re.search (JUNIOR_DETECTION, inputlines[k]) is not None or re.search (OTHER_DETECTION, inputlines[k]) is not None:
                #continue
            if re.search(NAME_ADDRESS_DETECTION,inputlines[k]) is not None:
                name_and_address = re.search(NAME_ADDRESS_DETECTION,inputlines[k])
                #print(re.findall(NAME_ADDRESS_DETECTION,inputlines[k]))
            elif re.search(NAME_ADDRESS_DETECTION_EXACT,inputlines[k]) is not None:
                name_and_address = re.search(NAME_ADDRESS_DETECTION_EXACT,inputlines[k])
                #print(re.findall(NAME_ADDRESS_DETECTION_EXACT,inputlines[k]))

            if name_and_address is not None or full_name is not None:
                #print("C",k,inputlines[k])

                if re.search(NAME_ADDRESS_DETECTION,inputlines[k]) is not None:
                    addr_origin = clean_address_single(name_and_address.group(11)+name_and_address.group(12))
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(NAME_ADDRESS_DETECTION_EXACT,inputlines[k]) is not None:
                    addr_origin = clean_address_single(name_and_address.group(8)+name_and_address.group(9))
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(EXTREME_TITLE_DETECTION,inputlines[k]) is not None:
                    col_address.append('')
                    newregister.append('')

                #try:
                #    line_for_information = inputlines[k] + re.search("(\[)(.*)", inputlines[k + 1]).group(2)
                #except:
                #    line_for_information = inputlines[k]

                die = 0
                try:
                    re.search(DEATHECTION, inputlines[k]).group(9)
                    die = 1
                except:
                    pass
                died.append(die)

                try:
                    foreign.append(re.search(FOREIGN_DETECTION, inputlines[k]).group(9))
                except:
                    foreign.append("No")

                clubs = []
                gradyear = ''
                college_complete = ''
                clubs_complete = []
                cityclubs = CITY_CLUBS[city]
                keys = list(cityclubs)
                for j in keys:
                    if "," in j:
                        j = j.replace(",", ".")
                    # club_full = re.findall(r"" + j + "(?=\.)|" + j + "(?=[0-9o][0-9o])|(?<=" + j + ")[0-9o][0-9o]", line)
                    club_full = re.findall(r"" + j + "(?=\.)|" + j + "[0-9o][0-9o]", inputlines[k])
                    if len(club_full) > 0:
                        clubs.append(club_full[0])
                        if re.search(r"" + j + "[0-9o][0-9o]", inputlines[k]) is not None:
                            uni = re.search(r"(" + j + "(?=[0-9o][0-9o]))", inputlines[k]).group(1)
                            if "'" not in uni:
                                uni = uni + "'"
                            grad_year_base = re.search(r"((?<=" + j + ")[0-9o][0-9o])", inputlines[k]).group(1)
                            if "o" in grad_year_base:
                                grad_year_base = grad_year_base.replace("o", "0")
                            if 1900 + int(grad_year_base) > int(year):
                                gradyear = str(1800 + int(grad_year_base))
                            else:
                                gradyear = str(1900 + int(grad_year_base))

                            try:
                                uni = CITY_CLUBS[city][uni]
                                college_complete = str(uni + ' ' + grad_year)
                            except:
                                pass
                        else:
                            try:
                                clubs_complete.append(CITY_CLUBS[city][j])
                            except:
                                pass
                if len(clubs) > 0:
                    clubs_raw.append(', '.join(clubs))
                else:
                    clubs_raw.append('')
                if len(clubs_complete) > 0:
                    clubs_clean.append(', '.join(clubs_complete))
                else:
                    clubs_clean.append('')
                grad_year.append(gradyear)
                college.append(college_complete)
                
                col_city.append(city)
                col_year.append(year)

                if re.search ("Married",inputlines[k]) is not None and full_name is not None and spouse_full_name is not None:
                    #print("Case1",full_name, inputlines[k])
                    col_lastname.append(add_spaces(full_name.group(1), "STRING"))
                    col_title.append(add_spaces(full_name.group(2), "STRING"))
                    first_and_middle_name = add_spaces(full_name.group(3), "LIST")
                    if len(first_and_middle_name) == 1:
                        col_middlename.append(' ')
                        col_firstname.append(first_and_middle_name[0])
                    elif len(first_and_middle_name) > 1:
                        col_firstname.append(first_and_middle_name[0])
                        col_middlename.append(' '.join(first_and_middle_name[1:]))
                        if len(first_and_middle_name[0]) == 1:
                            for m in range(len(first_and_middle_name[1:])):
                                if len(first_and_middle_name[m]) > 1:
                                    col_firstname.pop()
                                    col_firstname.append(first_and_middle_name[m])
                                    col_middlename.pop()
                                    col_middlename.append(' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:]))
                                    break

                    col_spouselast.append(add_spaces(spouse_full_name.group(1), "STRING"))
                    spouse_first_and_middle_name = add_spaces(spouse_full_name.group(3), "LIST")
                    if len(spouse_first_and_middle_name) == 1:
                        col_spousename.append(spouse_first_and_middle_name[0])
                        col_spousemiddle.append(' ')
                    elif len(spouse_first_and_middle_name) > 1:
                        col_spousename.append(spouse_first_and_middle_name[0])
                        col_spousemiddle.append(' '.join(spouse_first_and_middle_name[1:]))
                        if len(spouse_first_and_middle_name[0]) == 1:
                            for m in range(len(spouse_first_and_middle_name[1:])):
                                if len(spouse_first_and_middle_name[m]) > 1:
                                    #print(m, spouse_first_and_middle_name[m],' '.join(spouse_first_and_middle_name[:m] + spouse_first_and_middle_name[m + 1:]))
                                    col_firstname.pop()
                                    col_firstname.append(spouse_first_and_middle_name[m])
                                    col_middlename.pop()
                                    col_middlename.append(' '.join(spouse_first_and_middle_name[:m] + spouse_first_and_middle_name[m + 1:]))
                                    break

                    household += 1
                    col_household.append(household)
                    col_hhhead.append('1')
                    inputlines.pop(k+1)

                elif name_and_address is not None:
                    #print("Case2", name_and_address, inputlines[k])
                    col_lastname.append(add_spaces(name_and_address.group(1),"STRING"))
                    col_title.append(add_spaces(name_and_address.group(2),"STRING"))
                    first_and_middle_name = add_spaces(name_and_address.group(3),"LIST")
                    if len (first_and_middle_name) == 1:
                        col_middlename.append(' ')
                        col_firstname.append(first_and_middle_name[0])
                    elif len (first_and_middle_name) > 1:
                        col_firstname.append(first_and_middle_name[0])
                        col_middlename.append(' '.join(first_and_middle_name[1:]))
                        if len(first_and_middle_name[0]) == 1:
                            for m in range(len(first_and_middle_name[1:])):
                                if len(first_and_middle_name[m]) > 1:
                                    col_firstname.pop()
                                    col_firstname.append(first_and_middle_name[m])
                                    col_middlename.pop()
                                    col_middlename.append(' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:]))
                                    break

                    if name_and_address.group(7) is not None:
                        household += 1
                        col_household.append(household)
                        col_hhhead.append('1')
                        spouse_name = add_spaces(name_and_address.group(7),"LIST")
                        if len(spouse_name) == 1:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[0])
                            col_spousemiddle.append('')
                        elif len(spouse_name) == 2:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[1])
                            col_spousemiddle.append('')
                        elif len(spouse_name)> 2:
                            col_spousename.append(spouse_name[0])
                            col_spousemiddle.append(' '.join(spouse_name[1:-1]))
                            col_spouselast.append(spouse_name[-1])
                    else:
                        household += 1
                        col_household.append(household)
                        col_hhhead.append('0')
                        col_spousename.append('None')
                        col_spouselast.append('None')
                        col_spousemiddle.append('')

                elif full_name is not None:
                    #print("Case3", full_name, inputlines[k])
                    col_lastname.append(add_spaces(full_name.group(1), "STRING"))
                    col_title.append(add_spaces(full_name.group(2), "STRING"))
                    first_and_middle_name = add_spaces(full_name.group(3), "LIST")
                    household += 1
                    col_household.append(household)
                    col_hhhead.append('1')
                    if len(first_and_middle_name) == 1:
                        col_middlename.append(' ')
                        col_firstname.append(first_and_middle_name[0])
                    elif len(first_and_middle_name) > 1:
                        col_firstname.append(first_and_middle_name[0])
                        col_middlename.append(' '.join(first_and_middle_name[1:]))
                        if len(first_and_middle_name[0]) == 1:
                            for m in range(len(first_and_middle_name[1:])):
                                if len(first_and_middle_name[m]) > 1:
                                    col_firstname.pop()
                                    col_firstname.append(first_and_middle_name[m])
                                    col_middlename.pop()
                                    col_middlename.append(' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:]))
                                    break

                    if full_name.group(7) is not None:
                        spouse_name = add_spaces(full_name.group(7), "LIST")
                        if len(spouse_name) == 1:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[0])
                            col_spousemiddle.append('')
                        elif len(spouse_name) == 2:
                            col_spousename.append(spouse_name[0])
                            col_spouselast.append(spouse_name[1])
                            col_spousemiddle.append('')
                        elif len(spouse_name) > 2:
                            col_spousename.append(spouse_name[0])
                            col_spousemiddle.append(' '.join(spouse_name[1:-1]))
                            col_spouselast.append(spouse_name[-1])
                    else:
                        col_spousename.append('None')
                        col_spouselast.append('None')
                        col_spousemiddle.append('')

            k += 1

    if any(len(lst) != len(col_city) for lst in [newregister,col_city,col_year,col_lastname,col_title,col_middlename,col_firstname,col_spousename,col_spousemiddle,col_spouselast,col_address,col_household,col_hhhead,clubs_raw,clubs_clean,grad_year,foreign,died]):
        print("city:", col_city[-2:], "year:", col_year[-2:], "household_id:", col_household[-2:],
             "household_structure:", col_hhhead[-2:],
              "last_name:", col_lastname[-2:], "title:", col_title[-2:], "first_name:", col_firstname[-2:],
              "middle_names:", col_middlename[-2:],
             "spouse_name:", col_spousename[-2:], "spouse_middle_names:", col_spousemiddle[-2:], "spouse_last_name:", col_spouselast[-2:],
              "clubs_abbr:", clubs_raw[-2:], "clubs_extended:", clubs_clean[-2:], "grad_year:", grad_year[-2:],
              "foreign:", foreign[-2:], "died:", died[-2:], "address:", col_address[-2:], "new_register:",newregister[-2:])
        print ("city:", len(col_city), "year:", len(col_year), "household_id:", len(col_household), "household_structure:", len(col_hhhead),
                "last_name:", len(col_lastname), "title:", len(col_title), "first_name:", len(col_firstname), "middle_names:", len(col_middlename),
                "spouse_name:", len(col_spousename), "spouse_middle_names:", len(col_spousemiddle), "spouse_last_name:", len(col_spouselast),
                 "clubs_abbr:", len(clubs_raw), "clubs_extended:", len(clubs_clean), "grad_year:", len(grad_year), "foreign:", len(foreign),
                 "died:", len(died), "address:", len(col_address), "new_register:", len(newregister))
                                              
    return newregister, household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address


# In[17]:


def match_single(input_txt:str):
    
    inputtxt = open(input_txt, 'r', encoding="UTF-8")
    inputlines = inputtxt.readlines()
    #print("A",len(inputlines),inputlines)
    
    inputlines = clean_blank(inputlines)
    inputlines = general_cleaner(inputlines)
    inputlines = clean_line_single(inputlines)
    #print("B", len(inputlines), inputlines)
    newregister,household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address = generate_result_single(inputlines)


# In[19]:


##Set the path for the input txts of single line household
workdir = "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\"
csvpath = workdir+"csv_output_original\\"
for txtpath,txtdirs,_ in os.walk(workdir+"text_output_single"):
    for txtdir in txtdirs:
        city = re.findall(r"[A-z ]+(?= [0-9])", txtdir)[0]
        year = re.findall(r"[0-9]+", txtdir)[0] 
        
        col_city = []
        col_year = []
        col_lastname = []
        col_title = []
        col_middlename = []
        col_firstname = []
        col_spousename = []
        col_spousemiddle = []
        col_spouselast = []
        col_address = []
        col_household = []
        col_hhhead = []
        clubs_raw = []
        clubs_clean = []
        college = []
        grad_year = []
        foreign = []
        died = []
        newregister  = []
        household = int(household_dic[city+year])
        marriage = 0
        #household = 0
        
        for i in range(1,2000):
            input_txt = os.path.join(txtpath,city+' '+year,"pic"+str(i).zfill(3)+".txt")
            if os.path.exists(input_txt):
                match_single(input_txt)

        data = pd.DataFrame(
            {"city": col_city, "year": col_year, "household_id": col_household, "household_structure": col_hhhead,
             "last_name": col_lastname, "title": col_title, "first_name": col_firstname, "middle_names": col_middlename,
             "spouse_name": col_spousename, "spouse_middle_names": col_spousemiddle, "spouse_last_name": col_spouselast,
             "clubs_abbr": clubs_raw, "clubs_extended": clubs_clean, "college": college, "grad_year": grad_year, "foreign": foreign,
             "died": died, "address": col_address, "new_register":newregister})
        csvfile = csvpath+city+' '+year+".csv"
        data.to_csv(csvfile, mode='a+', index=False,  header=False)
        
        


# In[ ]:




