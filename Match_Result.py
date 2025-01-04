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
import pandas as pd

# In[3]:


# LIST_OF_TITLES is the building block for every single cleaning and match
# （）is to group the expressions; " in first and last place represents string; |is or; \the backward slash is Escape Character;
LIST_OF_TITLES = "M\&M\"|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|Mim|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More"

# EXPRESSIONS FOR CLEANING
# r represents original strings
# {1}is one re, {2,}is 2 or more re
# * is 0 or more; + is one or more
# goal: add space before and after parentheses
# include a group by (): can be used to extract later
PARENTHESES_AFTER_STRING = r"([A-Za-z]\()"
PARENTHESES_BEFORE_STRING = r"(\)[A-Za-z])"
SPACING_OF_HYPHENS = r"[a-z]*(\-)[A-Z]"  # -Unv. to identify university

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

NEW_TITLE_DETECTION = r"([^\s]+)\b( (M\&M\"|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More) )([A-Za-z ]*)( )?(\(([^\)\(]+)\))?"

# THIS ONE BELOW DOES NOT NEED TO HAVE SPACES BETWEEN TITLES, AND STILL WORKS IF THERE ARE MUTLIPLE SPACES!
# EXTREME_TITLE_DETECTION = r"([^(\s]+)\b( (M\&M\"|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More) )([A-Za-z ]*)( )?(\(([^)]+)\))?"
# r"([^(\s]+)\b( (M\&M\"|Mine|Lt\&M\"|M\&MW\"|MÃ†N\"\*|NÃ†N\"|Gen\&M\"|Gen\&M\'|Ct\&Ctss|Col\&Mâ€œ|Hon\&M\"|Hon\&M\*\*|Capt \& N\"|Capt\&N\"|Capt \& N\*\*|Col \& N\"|Brig Gen \& N\"|Maj \& M\*\*|Min|D&M\"\*|MIN\"|NEN\"|NAN\"|D&N\"|Niss|NAM\"|M&M'\*|N&N\"|NEM\"|M&M''|M&M\*\*|M&N|M'|M\"|'|\"|D\"|N'|M\&M“|D'|MAN\"|M\&M\"|M&M”|D&M\"|MEM\"|M\\&ME|M&M\*|M\&M\"\*|MM\"|M&M|M's|Lt\&M\"|Gen\&M\"|Ct\&Ctss |\nM\"|\||MEM\"|M\&M”|M™|MT|\&M\*|\*|M\&M|M\-|MEM\"|I\"|I'|MIM\"|MAM\"|Mam\"|M\*|M“|D&M“|&M\"|1\"|N&M\"|Man\"|M.M\"|M'|N\"|Mº|M J|M\&M™|M\&M'|MEN”|\&MMEN|D\&M\*|M|D\&M|D\&M”|\-|Miss|Mis|Mo\"|Mi|Mb|Misé|Misses|Me|MxM™|MEM\*|M8s|Hon&M“|Ms|MEN“|Man”|M's|Nisses|M&N\"|MⓇ|Män“|DÆM\"|D’|D&M\*\*|MIN”|l'|M°|Mik”|M&N”|&M“|M\*\*\*|Mr|Mom|\*\*|W&M\"|W&M“|l\"|\| ™|r\"|Ms\&Mis|Mwen|Mľ|Milla|Mo|Mama|Mie|M\*\*|NIM”|Mim\"|Misce|M\".|Mrs|/\*|MM“|les|\\\"\*|N\*\*|Nº|\\\"|Mens|I™|M&MW|MV|MEN\"|\!\"|More) )([A-Za-z ]*)( )?(\(([^)]+)\))?"


CORRECT_TITLES = {
    'Mr': ["M'", "N'", "M", "N", 'M-', "I'", '1*', 'Mº', 'Mr', 'N°', 'MF', 'W','№¹'],
    'Mrs': ['Mrs', 'M"', "M's", 'MT', 'I"', 'M*', '1**', '1"', 'N"', 'M**', 'M".', 'Mrs', 'N**', 'I™', 'N™', "Mâ€œ",'M³','M™',"l'","№",'Mª'],
    'Mr&Mrs': ["Mr&Mrs", 'M&M"', 'MIN"', 'NEN"', 'NAN"', 'NEN"NAN"','NAM"', "M&M'*", 'N&N"', 'NEM"', "M&M''", "M&M**", 'M&N',
               "M&M'", 'MAN"', 'MEM"', "M&ME", "M&M*", 'M&M"*', 'MM"', 'M&M', 'N&MT', 'MIM"', 'MAM"', "'MN",'Mam"', 'N&M"',
               'Man"', 'M.M"', "M&M™", 'MEN"', "MxM™", 'MEM*', 'M&N"', 'Män"', 'MIN"', 'MIM', 'MIN', 'NIN', 'NIM',
               'MEM', 'NEM', 'MEN', 'NEN', '&','Mik"', 'Mom', 'W&M"', 'NIM"', 'Mim"', "M&MW", 'MÃ†N"*', 'NÃ†N"', 'MIN"',
               'MIM"', 'NAN', 'NAM', 'MAN', 'MAM', 'MM', '&M', 'M&M','VN"','MAMA','M&','MaM"','Mil','MTS','M&Ms',' N&N"','M&'],
    'Dr&Mrs': ['Dr&Mrs', 'D&M"*', 'D&N"', 'D&M"', 'D&M*', 'D&M', 'DÆM"', 'D&M**', 'DaN', 'Da N',"DM",'D&M','Da','DAM"'],
    'Dr': ['Dr', 'D"', "D'",'D'],
    'Miss': ['Min', 'Niss', 'Miss', 'Mis', 'Mo"', 'M8s', 'Mie', 'Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins', 'Viss',
             'M¹', 'Mi','Mia','MSTS','M¹"','N¹'],
    'Misses': ['Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'lisses','Mise'],
    'Msrs': ['Msrs', 'Ms', 'Mb', 'Me', 'M***', 'Mens', 'Nissen','MS'],
    'Lt&Mrs': ['Lt&Mrs', 'Lt&M"'],
    'Lt': ['Lt'],
    'Gen&Mr': ["Gen&Mr", "Gen&M'"],
    'Gen&Mrs': ["Gen&Mrs", 'Gen&M"'],
    'Ct&Ctss': ['Ct&Ctss'],
    'Hon&Mrs': ["Hon&Mrs", 'Hon&M"', 'Hon&M**'],
    'Capt&Mrs': ['Capt&Mrs', 'Capt & N"', 'Capt&N"', 'Capt & N**'],
    'Maj&Mrs': ['Maj&Mrs', 'Maj & M**'],
    'BrigGen&Mrs': ['BrigGen&Mrs', 'Brig Gen & N"'],
    'Col&Mrs': ['Col&Mrs', 'Col & N"', 'Col&Mâ€œ','Col&M"'],
    'Rev': ['Rev'],
    'Col': ['Col'],
    'Capt': ['Capt'],
    'Maj': ['Maj'],
    'LtCol&Mrs': ['LtCol&Mrs','LtCol&M"'],
    'Prof': ['Prof'],
    'RevDr&Mrs': ['RevDr&Mrs', 'Rev"','Rev Dr&Mrs' ],
    'Lt&Cdr' : ['Lt&Cdr', 'LtCdr'],
    'Cdr&Mrs': ['Cdr&Mrs','Cdr&M"'],
    'Cdr' : ['Cdr'],
    'Ens' : ['Ens'],
    'Judge&Mrs': ['Judge&Mrs','Judge and Mrs']
}

HH_TITLES = ['Mr&Mrs', 'M&M\\"', 'MIN\\"', 'NEN\\"', 'NAN\\"','NEN\\"NAN\\"', 'NAM\\"', "M&M\\'\\*", 'N&N\\"', 'NEM\\"',
             "M&M\\'\\'", 'M&M\\*\\*','M&N', 'M&M\\"', 'MAN\\"', 'MEM\\"', 'M&ME', 'M&M\\*', 'M&M\\"\\*', 'MM\\"', 'M&M',
             'N&MT', 'MIM\\"', 'MAM\\"', '&','Mam\\"', 'N&M"', 'Man\\"', 'M\\.M"', 'M\\&M™', 'MEN\\"', 'MxM™', 'MEM\\*',
             'M&N\\"', 'Män\\"', 'MIN\\"', 'Mik\\"', 'MIM', 'MIN', 'NIN', 'NIM', 'MEM', 'NEM', 'MEN', 'NEN', 'MAM',
             'Mom', 'W\\&M"', 'NIM"', 'Mim"', 'M&MW', 'MÃ†N\\"\\*', 'NÃ†N\\"', 'MIN\\"', 'MIM\\"', 'NAN', 'NAM', 'MAN',
             'Dr\\&Mrs', 'D\\&M"\\*', 'D\\&N"', 'D\\&M"','D\\&M\\*', 'D\\&M', 'DÆM"', 'D\\&M\\*\\*', 'DaN',
             'Lt\\&Mrs', 'Lt\\&M"', "Gen\\&M'", 'Gen\\&Mrs', 'Gen\\&M"', 'LtCol\\&Mrs',
             'Ct\\&Ctss', 'Hon\\&Mrs', 'Hon\\&M"', 'Hon\\&M\\*\\*', 'Capt\\&Mrs', 'Capt\\ \\&\\ N"', 'Capt\\&N"',
             'Capt\\ \\&\\ N\\*\\*', 'Maj\\&Mrs', 'Maj\\ \\&\\ M\\*\\*', 'BrigGen\\&Mrs', 'Brig\\ Gen\\ \\&\\ N"',
             'Col\\&Mrs', 'Col\\ \\&\\ N"', 'Col\\&Mâ€œ', '"', 'Col&M"','RevDr&Mrs', 'Rev"',"DM",'D&M','M&Ms',' N&N"',
             'MM', '&M', 'M&M','VN"','MAMA','M&','Da','MaM"',"Mil",'MTS','Lt&Cdr','LtCdr','Cdr&Mrs','Cdr&M"','LtCol&M"',
             'Rev Dr&Mrs','DAM"','M&','Judge&Mrs','Judge and Mrs']

JUNIOR_TITLES = ['Mr', 'Miss', 'Misses', 'Msrs',
                 "M\\'", "N\\'", "M", "N", 'M\\-', "I\\'", '1\\*', 'Mº', 'Mr', 'N°', 'MF',
                 'M\\"', "M\\'s", 'MT', 'I\\"', 'M\\*', '1\\*\\*', '1\\"', 'N\\"', 'M\\*\\*', 'M\\"\\.',
                 'N\\*\\*', 'I™', 'N™' "Mâ€œ",'M³', 'M¹', 'Dr', 'D\\"', "D\\'",
                 'Min', 'Niss', 'Mis', 'Mo\\"', 'M8s', 'Mie', 'Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins', 'Viss','Mi',
                 'Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'Mise', 'lisses', 'Ms', 'Mb', 'Me', 'M\\*\\*\\*', 'Mens', 'Nissen',
                 "'", 'W', 'MS','№¹','№','Mia','Mª','MSTS','M¹"','N¹']

OTHER_TITLES = ['Mr&Mrs', 'M&M\\"', 'MIN\\"', 'NEN\\"', 'NAN\\"','NEN\\"NAN\\"', 'NAM\\"', "M&M\\'\\*", 'N&N\\"', 'NEM\\"',
                "M&M\\'\\'", 'M&M\\*\\*','M&N', 'M&M\\"', 'MAN\\"', 'MEM\\"', 'M&ME', 'M&M\\*', 'M&M\\"\\*', 'MM\\"', 'M&M',
                'N&MT', 'MIM\\"', 'MAM\\"', '&','Mam\\"', 'N&M"', 'Man\\"', 'M\\.M"', 'M\\&M™', 'MEN\\"', 'MxM™', 'MEM\\*',
                'M&N\\"', 'Män\\"', 'MIN\\"', 'Mik\\"', 'MIM', 'MIN', 'NIN', 'NIM', 'MEM', 'NEM', 'MEN', 'NEN', 'MAM',
                'Mom', 'W\\&M"', 'NIM"', 'Mim"', 'M&MW', 'MÃ†N\\"\\*', 'NÃ†N\\"', 'MIN\\"', 'MIM\\"', 'NAN', 'NAM', 'MAN',
                'Dr\\&Mrs', 'D\\&M"\\*', 'D\\&N"', 'D\\&M"','D\\&M\\*', 'D\\&M', 'DÆM"', 'D\\&M\\*\\*', 'DaN',
                'Lt\\&Mrs', 'Lt\\&M"', 'Gen\\&Mr', "Gen\\&M'", 'Gen\\&Mrs', 'Gen\\&M"', 'LtCol\\&Mrs',
                'Ct\\&Ctss', 'Hon\\&Mrs', 'Hon\\&M"', 'Hon\\&M\\*\\*', 'Capt\\&Mrs', 'Capt\\ \\&\\ N"', 'Capt\\&N"',
                'Capt\\ \\&\\ N\\*\\*', 'Maj\\&Mrs', 'Maj\\ \\&\\ M\\*\\*', 'BrigGen\\&Mrs', 'Brig\\ Gen\\ \\&\\ N"',
                'Col\\&Mrs', 'Col\\ \\&\\ N"', 'Col\\&Mâ€œ',
                'Mr', 'Miss', 'Misses', 'Msrs',
                "M\\'", "N\\'", "M", "N", 'M\\-', "I\\'", '1\\*', 'Mº', 'Mr', 'N°', 'MF',
                'M\\"', "M\\'s", 'MT', 'I\\"', 'M\\*', '1\\*\\*', '1\\"', 'N\\"', 'M\\*\\*', 'M\\"\\.',
                'N\\*\\*', 'I™', 'N™' "Mâ€œ",'M³', 'M¹', 'Dr', 'D\\"', "D\\'",
                'Min', 'Niss', 'Mis', 'Mo\\"', 'M8s', 'Mie', 'Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins', 'Viss','Mi',
                'Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'Mise', 'lisses', 'Ms', 'Mb', 'Me', 'M\\*\\*\\*', 'Mens', 'Nissen',
                'Dr', 'D"', "D'", 'Lt', 'Rev', 'Col','Capt', 'Maj','Prof',"'", '"', 'Col&M"','RevDr&Mrs', 'Rev"',"DM",
                'D&M', 'MM', '&M', 'M&M','VN"','MAMA','M&','W','M™','Da','D',"l'",'MaM"','Mil','MS','№¹','MTS','№',
                'Lt&Cdr','LtCdr','Cdr','Ens','Mia','Cdr&Mrs','Cdr&M"','LtCol&M"','M&Ms','Mª','Rev Dr&Mrs',' N&N"','MSTS',
                'DAM"','M¹"','M&','N¹','Judge&Mrs','Judge and Mrs']

DOUBLE_TITLES = ['Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'lisses', 'Mise',
                'Msrs', 'Ms', 'Mb', 'Me', 'M\\*\\*\\*', 'Mens', 'Nissen',
                 'The Misses', 'The Misé', 'The Mises','The Nisses', 'The lisses', 'The Mise',
                 'Min', 'Niss', 'Miss', 'Mis', 'Mo"', 'M8s', 'Mie', 'Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins',
                 'Viss','M¹', 'Mi', 'Mia','Miss','N¹',
                 "M'", "N'", "M", "N", 'M-', "I'", '1*', 'Mº', 'Mr', 'N°', 'MF', 'W','№¹','Mr','MSTS']

ALL_TITLES = ['Mr&Mrs', 'M&M\\"', 'MIN\\"', 'NEN\\"', 'NAN\\"','NEN\\"NAN\\"', 'NAM\\"', "M&M\\'\\*", 'N&N\\"', 'NEM\\"',
              "M&M\\'\\'", 'M&M\\*\\*','M&N', 'M&M\\"', 'MAN\\"', 'MEM\\"', 'M&ME', 'M&M\\*', 'M&M\\"\\*', 'MM\\"', 'M&M',
              'N&MT', 'MIM\\"', 'MAM\\"', '&','Mam\\"', 'N&M"', 'Man\\"', 'M\\.M"', 'M\\&M™', 'MEN\\"', 'MxM™', 'MEM\\*',
              'M&N\\"', 'Män\\"', 'MIN\\"', 'Mik\\"', 'MIM', 'MIN', 'NIN', 'NIM', 'MEM', 'NEM', 'MEN', 'NEN', 'MAM',
              'Mom', 'W\\&M"', 'NIM"', 'Mim"', 'M&MW', 'MÃ†N\\"\\*', 'NÃ†N\\"', 'MIN\\"', 'MIM\\"', 'NAN', 'NAM', 'MAN',
              'Dr\\&Mrs', 'D\\&M"\\*', 'D\\&N"', 'D\\&M"','D\\&M\\*', 'D\\&M', 'DÆM"', 'D\\&M\\*\\*', 'DaN',
              'Lt\\&Mrs', 'Lt\\&M"', 'Gen\\&Mr', "Gen\\&M'", 'Gen\\&Mrs', 'Gen\\&M"', 'LtCol\\&Mrs',
              'Ct\\&Ctss', 'Hon\\&Mrs', 'Hon\\&M"', 'Hon\\&M\\*\\*', 'Capt\\&Mrs', 'Capt\\ \\&\\ N"', 'Capt\\&N"',
              'Capt\\ \\&\\ N\\*\\*', 'Maj\\&Mrs', 'Maj\\ \\&\\ M\\*\\*', 'BrigGen\\&Mrs', 'Brig\\ Gen\\ \\&\\ N"',
              'Col\\&Mrs', 'Col\\ \\&\\ N"', 'Col\\&Mâ€œ',
              'Mr', 'Miss', 'Misses', 'Msrs',
              "M\\'", "N\\'", "M", "N", 'M\\-', "I\\'", '1\\*', 'Mº', 'Mr', 'N°', 'MF',
              'M\\"', "M\\'s", 'MT', 'I\\"', 'M\\*', '1\\*\\*', '1\\"', 'N\\"', 'M\\*\\*', 'M\\"\\.',
              'N\\*\\*', 'I™', 'N™' "Mâ€œ",'M³', 'M¹', 'Dr', 'D\\"', "D\\'",
              'Min', 'Niss', 'Mis', 'Mo\\"', 'M8s', 'Mie', 'Mies', 'Mama', 'y', 'fis', 'Ni', 'Vi', 'Mins', 'Viss','Mi',
              'Misses', 'Misé', 'Nisses', 'Mine', 'Mises', 'lisses', 'Ms', 'Mb', 'Me', 'M\\*\\*\\*', 'Mens', 'Nissen',
              'Dr', 'D"', "D'", 'Lt', 'Rev', 'Col','Capt', 'Maj','Prof','"',"'",'Col&M"', 'RevDr&Mrs', 'Rev"',"DM",'D&M',
              'MM', '&M', 'M&M','VN"','MAMA','M&','W','M™','Da','D',"l'",'MaM"','Mil','MS','№¹','№','MTS','Lt&Cdr',
              'LtCdr','Cdr','Ens','Mia','Cdr&Mrs','Cdr&M"','LtCol&M"','M&Ms','Mª','Mise','Rev Dr&Mrs', ' N&N"','MSTS',
              'DAM"','M¹"','M&','N¹','Judge&Mrs','Judge and Mrs']

NAME_ABBRV = {
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
    "Arch'd": "Archibald",
    "Rich'd": "Richard",
    "Fred'k": "Frederick",
    "Fred'c": "Frederic",
    "Dan'l": "Daniel",
    "Sam'l": "Samuel",
    "Sam'1": "Samuel"
}

CORRECT_ADDRESS = {
    '10': ['I\s*O'],
    '110': ['I\s*IO', 'I\s*10'],
    '111': ['I\s*II'],
    '11': ['I\s*I'],
    '1110': ['I\s*I\s*I\s*O'],
    '101': ['I\s*OI'],
    '120': ['I\s*20'],
    '190': ['I\s*9\s*o'],
    '00': ['\s*O\s*O\s*'],
    'I11': ['Ill'],
    '1': ['\sI\s'],
    '0': ['\sO\s']
}

CORRECT_LETTERS = {
    'A': ['Á', 'À', 'Â', 'Ä', 'Ã', 'Å', 'Ā', 'Ą', 'Ă'],
    'a': ['á', 'à', 'â', 'ä', 'ã', 'å', 'ā', 'ą', 'ă'],
    'C': ['Ç', 'Ć', 'Č', 'Ĉ', 'Ċ'],
    'c': ['ç', 'ć', 'č', 'ĉ', 'ċ'],
    'D': ['Đ', 'Ď'],
    'd': ['đ', 'ď'],
    'E': ['É', 'È', 'Ê', 'Ë', 'Ē', 'Ę', 'Ě', 'Ĕ', 'Ė'],
    'e': ['é', 'è', 'ê', 'ë', 'ē', 'ę', 'ě', 'ĕ', 'ė'],
    'G': ['Ğ', 'Ĝ', 'Ġ', 'Ģ'],
    'g': ['ğ', 'ĝ', 'ġ', 'ģ'],
    'H': ['Ĥ', 'Ħ'],
    'h': ['ĥ', 'ħ'],
    'I': ['Í', 'Ì', 'Î', 'Ï', 'Ī', 'Į', 'İ', 'Ĭ', 'Ĩ'],
    'i': ['í', 'ì', 'î', 'ï', 'ī', 'į', 'ı', 'ĭ', 'ĩ'],
    'J': ['Ĵ'],
    'j': ['ĵ'],
    'K': ['Ķ'],
    'k': ['ķ', 'ĸ'],
    'L': ['Ł', 'Ĺ', 'Ľ', 'Ļ', 'Ŀ'],
    'l': ['ł', 'ĺ', 'ľ', 'ļ', 'ŀ'],
    'N': ['Ñ', 'Ń', 'Ň', 'Ņ', 'Ŋ'],
    'n': ['ñ', 'ń', 'ň', 'ņ', 'ŋ'],
    'O': ['Ó', 'Ò', 'Ô', 'Ö', 'Õ', 'Ø', 'Ō', 'Ő', 'Ŏ'],
    'o': ['ó', 'ò', 'ô', 'ö', 'õ', 'ø', 'ō', 'ő', 'ŏ'],
    'R': ['Ř', 'Ŕ', 'Ŗ'],
    'r': ['ř', 'ŕ', 'ŗ'],
    'S': ['Š', 'Ś', 'Ş', 'Ŝ'],
    's': ['š', 'ś', 'ş', 'ŝ'],
    'T': ['Ť', 'Ţ', 'Ŧ'],
    't': ['ť', 'ţ', 'ŧ'],
    'U': ['Ú', 'Ù', 'Û', 'Ü', 'Ū', 'Ů', 'Ű', 'Ŭ', 'Ũ', 'Ų'],
    'u': ['ú', 'ù', 'û', 'ü', 'ū', 'ů', 'ű', 'ŭ', 'ũ', 'ų'],
    'W': ['Ŵ', 'Ẁ', 'Ẃ', 'Ẅ'],
    'w': ['ŵ', 'ẁ', 'ẃ', 'ẅ'],
    'Y': ['Ý', 'Ŷ', 'Ÿ', 'Ỳ'],
    'y': ['ý', 'ŷ', 'ÿ', 'ỳ'],
    'Z': ['Ž', 'Ź', 'Ż'],
    'z': ['ž', 'ź', 'ż']
}


# The very first name: title (EG: Mrs. Mr. Dr. Rev.) + name; or name; or title (EG: Dr) + name; group(1)
#Avoid the juniors(may start with Jun..etc) that is wrongly captured as lastnames, especially for Dutch lastname
base_pattern = '(^[AIK-Z][a-z][a-z]? [A-Z][a-z]+|^[A-Z][A-Za-z\-]+|^[A-Z][A-Za-z\']+|^[dv][aeuo][nr]? [A-Z][a-z]+) ('
lastname_pattern = '^[AIK-Z][a-z][a-z]? [A-Z][a-z]+|^[A-Z][A-Za-z\-]+|^[A-Z][A-Za-z\']+|^[dv][aeuo][nr]? [A-Z][a-z]+'
# General expressions to match titles; group(2)
title_patterns = ['[\w ]+Col ?& ?\S+', '[A-Z0-9]+\W+', '[A-Z][a-z]\W+', '[A-Z][a-z][a-z]\W+', '[A-Z][a-z]* ?& ?\S+',
                  '[A-Z][A-z][A-z]\W+[A-Z]+', '[A-Z][a-z]+\W+ Mrs ', '[A-Z][a-z][a-z] ?[\&A-Z]+\W',
                  '\S+â€œ', '\S+â€™', '\S+â€', '\S+¢', 'Lt', 'Mr', 'Mrs', 'Miss', 'Mom', 'Misses', 'Capt', 'M', 'N',
                  'Mis', 'The Misses', 'The Nisses',
                  '[^\w\.]+', '\\\"', '[MNV][a-z]', "fis", 'Viss', 'Maj Gen', 'Maj', 'Capt\S+',
                  'Mises', 'Col', 'Rev', '[A-Z][a-z][a-z] ?[\&A-Z]+[a-z]?\W+[A-Z]+[a-z]?', 'Mia', 'lisses', 'Ms',
                  '[A-Z][a-z][A-Z]\W+', 'Mama', 'y', '[A-z]y', 'Y', 'Mi[a-z][a-z]', '\w\W+', '[A-Z]\W+[A-Z]', "Nisses",
                  "[\'\"]?[MN]{1,2}[\'\"]?", '[A-Z][a-z][A-Z][a-z]', '[A-Z][A-Z]', 'flases', '[MNVH][iao][easn]',
                  '[A-Z][a-z][a-z]? ?[\&A-Z]+[a-z]+\W+[A-Z]+[a-z]?\W?\W?',
                  '[A-Z][a-z]\W+[A-Z][a-z][a-z][a-z]', '[A-z]+[^\w ]+[A-z]+\W+', 'M I M', 'MIM']
#Matching order: from the left to the right
full_pattern = base_pattern + '|'.join(title_patterns) + '|' +'|'.join(ALL_TITLES) + '|' + LIST_OF_TITLES + ')'
full_and_spouse_name = r"( )+((\(?[A-Z][A-Za-z0-9' ]+\*?\)?)(?=( )?\-[A-Z][a-z]?[a-z]?\.)|(\(?[A-Z][A-Za-z0-9' ]+\*?\)?)(?=[\s\.]*)|(\(?[A-Z][A-Za-z0-9' ]+\*?\)?))(( )?(\(([A-Z][A-Za-z0-9 \-\']+)\)))?(\s?\-?[A-Za-z0-9\'\"\-\.\& ]*)"
full_name_junior = r"(([A-Z][A-Za-z0-9' ]+\*?)(?=( )?\-[A-Z][a-z]?[a-z]?\.)|([A-Z][A-Za-z0-9' ]+\*?)(?=[\s\.]*)|([A-Z][A-Za-z0-9' ]+\*?))(\s?\-?[A-Za-z0-9\'\"\-\. ]*)"
full_name_other = r"(((\(?[A-Z][A-Za-z0-9' ]+\*?\)?)(?=[\s\.]*)|(\(?[A-Z][A-Za-z0-9' ]+\*?\)?))(( )?\(([A-Z][A-Za-z0-9 \-']+)\)( )?)?)(\s?\-?[A-Za-z0-9\'\"\-\. ]*)"
full_name_double = r"(([A-Z][A-Za-z0-9' ]+\*?)(?=( )?\-[A-Z][a-z]?[a-z]?\.)|([A-Z][A-Za-z0-9' ]+\*?)(?=[\s\.]*)|([A-Z][A-Za-z0-9' ]+\*?))(\s?\-?[A-Za-z0-9\'\"\-\. ]*)"
# The full titles including household's name and wife's name
# xxx(?=pattern): match the whole xxxpattern, but only catch xxx;
# (multiple)name separate with spaces+ (optional) a word with 2-3 letters end with .; or a sequence of zero or more letters or spaces, followed by an optional asterisk character
# + (optional) space+ (optional)name &- &' in parentheses
# group(3) = household name after title, group(4)= wife name including space and patentheses, group(7)= wife name in parentheses
EXTREME_TITLE_DETECTION = full_pattern + full_and_spouse_name
NOTITLE_DETECTION = r"^(([A-Z][A-Za-z]+\s+[A-Z][A-Za-z0-9']+\s*[A-Za-z0-9' ]*\*?)(?=( )?\-[A-Z][a-z]?[a-z]?\.)|" \
                    r"([A-Z][A-Za-z]+\s+[A-Z][A-Za-z0-9']+\s*[A-Za-z0-9' ]*\*?)(?=[\s\.]*)|" \
                    r"([A-Z][A-Za-z]+\s+[A-Z][A-Za-z0-9']+\s*[A-Za-z0-9' ]*\*?))"\
                    r"(( )?(\(([A-Z][A-Za-z0-9 \-\']+)\)))?(\s?\-?[A-Za-z0-9\'\"\-\.\& ]*)"
MULTIPLE_DETECTION = base_pattern + '|'.join(DOUBLE_TITLES)+ '|' + '|'.join(OTHER_TITLES)+ ') ' + full_name_double + '.* & '\
                     +'(' + '|'.join(DOUBLE_TITLES)+ '|' + '|'.join(OTHER_TITLES)+ ') '+ full_name_double
junior = "^([jJ][pniourgsl]+|There|Jr|J|Jos|Ju|Jun|Jars|Jons|Jiors|Jori|Jis|Ji|Jirs|JTS|JNE|JN|J'|JE|Jun,|Jurs|Jan) "
junior_middle = "(Juniors|juniors|Junior|junior|There|Jr|J|Jos|Ju|Jun|Jars|Jons|Jiors|Jori|Jis|Ji|Jirs|JTS|JNE|JN|J'|JE|Jun,|Jurs|Jan) "
JUNIOR_DETECTION = junior + '(('+ '|'.join(JUNIOR_TITLES) + '|' + LIST_OF_TITLES +') )'+ full_name_junior\
+ '(& (('+ '|'.join(JUNIOR_TITLES) + '|' + LIST_OF_TITLES + ') )?'+ full_name_junior + ')?'\
+ '(& (('+ '|'.join(JUNIOR_TITLES) + '|' + LIST_OF_TITLES + ') )?'+ full_name_junior + ')?'
OTHER_DETECTION = '(^((' + '|'.join(OTHER_TITLES) + '|' + LIST_OF_TITLES + ') )' + full_name_other + ')'\
+ '(& ((' + '|'.join(OTHER_TITLES) + '|' + LIST_OF_TITLES + ') )?' + full_name_other + ')?'\
+ '(& ((' + '|'.join(OTHER_TITLES) + '|' + LIST_OF_TITLES + ') )?' + full_name_other + ')?'
OTHER_JUNIOR_DETECTION =base_pattern + '|'.join(OTHER_TITLES) + '|' + LIST_OF_TITLES + ') ' + full_name_other\
+ '.* & ' + junior_middle + '('+'|'.join(JUNIOR_TITLES) + '|' + LIST_OF_TITLES + ') '+ full_name_junior
ADDRESS_DETECTION = r"(([\.]{2,}|[\. ]{2,})(.*)([A-Za-z0-9\'\"\-\s]+))"
ADDRESS_DETECTION_EXACT = r"(\w[ ]*[0-9]{1,3}[ ]*[A-Z][ ]*[0-9]{1,3}|[0-9]{1,3}[ ]*[A-Z][ ]*[A-Za-z\'\-]|[0-9]{1,4}[ ]*[A-Za-z\'\-]+\s?[A-Za-z\'\-]+[ ]*Sq|[0-9]{1,4}[ ]*[A-Za-z\'\-]+\s?[A-Za-z\'\-]+[ ]*St[ ]*[A-Za-z\'\-]+\s?[A-Za-z\'\-]+|[0-9]{1,4}[ ]*St[A-Za-z\'\-]+|[0-9]{1,4}[ ]*[A-Za-z\'\-]+\s?[A-Za-z\'\-]+[ ]*Av|[0-9]{1,3}.+NY|[0-9]{1,3}.+NJ|[0-9]{1,3}.+DC|[0-9]{1,3}.+N Y|[0-9]{1,3}.+N J)"
NAME_ADDRESS_DETECTION = EXTREME_TITLE_DETECTION + r'(.*)' + ADDRESS_DETECTION
NAME_ADDRESS_DETECTION_EXACT = EXTREME_TITLE_DETECTION + r'(.*)' + ADDRESS_DETECTION_EXACT
NOTITLE_ADDRESS_DETECTION = NOTITLE_DETECTION+ r'(.*)' + ADDRESS_DETECTION
NOTITLE_ADDRESS_DETECTION_EXACT = NOTITLE_DETECTION+ r'(.*)' + ADDRESS_DETECTION_EXACT
MULTIPLE_ADDRESS_DETECTION = MULTIPLE_DETECTION+ r'(.*)' + ADDRESS_DETECTION
MULTIPLE_ADDRESS_DETECTION_EXACT = MULTIPLE_DETECTION+ r'(.*)' + ADDRESS_DETECTION_EXACT
FOREIGN_DETECTION = EXTREME_TITLE_DETECTION + r"(.+)(London|Rome|Paris|Italy|France|Germany|Ireland)"
FOREIGN = r"(London|Rome|Paris|Italy|France|Germany|Ireland|Eng)"
DEATHECTION = EXTREME_TITLE_DETECTION + r"(.+)(Died)"
TIME = r"(=?.*)(Jan|Feb|Mar|Mch|Mcn|Apr|May|Jun|Jul|Jly|Aug|Sep|Oct|Nov|Dec)([a-z]*)(\s*)([0-9]{1,2})?"
TRIVIAL = r"\-|'{2,}|\"|\||^I\s|\[|\."
NONASCII = r"[^A-z0-9\s\']+"
PHONE = r"([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|" \
        r"Dhone  Ph|No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|" \
        r"Phon|phop|Phone|phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|po|op|no|ne|P| o|p|e|g|i|f|w|d|r)(\s*)" \
        r"([0-9]+[A-Za-z]*)(\s*)(f Mt V|k Mt V|Mt V|W Mt V|IO W|B B |Tux)"
PHONE2 = r"([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|" \
         r"Dhone  Ph|No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|" \
         r"Phon|phop|Phone|phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|po|op|no|ne|P| o|p|e|g|i|f|w|d|r)(\s*)([0-9]+[A-Za-z]*)"
PHONE3 = r"^([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|Dhone  Ph|" \
         r"No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|Phon|phop|Phone|" \
         r"phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|ne|P| o|p|po|op|no|g|e|ho|i|f|w|d|r|u|V|Q|j|J|f Mt V|k Mt V|Mt V|" \
         r"W Mt V|IO W|B B |Tux|Pros)\s+"
PHONE4 = r"^([PpDhoNnefgr:%\s]+|hone phop|Pho hope|hope  No|hone Pho|No phopo Ph|phopo|ph Phone|one Pho|No  Ph|Dhone  Ph|" \
         r"No  Phono|hope  Ph|of P|Dhone  Pho|Phono  No|phope  N|ne  No|ag  ho|Dhone|Phoe|Phop|phopo|Phope|Phon|phop|Phone|" \
         r"phone|hone|No  ne|No|phro|Ph|Php|Ph%|Ph:|Pho|one|ne|P| o|p|po|op|no|g|e|ho|i|f|w|d|r|u|V|Q|j|J|f Mt V|k Mt V|Mt V|" \
         r"W Mt V|IO W|B B |Tux|Pros)$"
OTHER = r"Died.*|sa tog|Club|Married.*"
OTHER2 = r"^(')?\s*\w+\s*$|^\s*\d+\s*$"
ELSE = r"absent|Absent|abroad|Abroad|Ab'd|avd|abd|Av'd|av'd|ab'd|at'l|atl"
MOVE = r"(see)(.*)|(See)(.*)"
BRACKET = r"「|」|\["
# The line belongs to previous line
LINE_AFTER_PREV = r"^\(.*\)|^(\s*[\.]+)|^(\s*[\. ]+)|^(\s*[0-9]+)|^(\s*[A-Z][a-z]?[a-z]?\.)|^(\s*[A-Z][a-z]?[a-z]?\')|" \
                  r"^(\s*Uv(\.)?)|^(\s*Un\.)|^(\s*Ui(\.)?)|^(\s*UI(\.)?)|^(\s*Phone)|^(\s*Rf(\.)?)|^(\s*Ph(\:)?\s*[0-9])" \
                  r"^(\s*Php(\:)?\s*[0-9])|^(\s*Pho(\:)?\s*[0-9])|^(\s*P\s*[0-9])|^ab\'d"
next_line_club = r"^[A-Z][a-z](?=\.)|^[A-Z][a-z][a-z](?=\.)|^[A-Z]+\'|^(?<=[A-Z]\')[0-9]+|^[A-Z]+(?=\.)|^[^\(\[]+\)|^\.|^ \."
next_line_other = r"(London|Rome|Paris|Italy|England|France|Germany|Ireland|Died)"
suffix = ["Jr", "2d", "3d", "4th", "Sr", "2nd", "3rd", "3d","2d","5th", "6th"]
surname = ["Mc","De","Du","La","de","du","Le","le","O'","St","Del","St","del","Des","des","Der","der","El","el",
           "d'", "L'","D'"]

#Import the clubs
with open("city_clubs_updated.txt", 'r') as f:
    content = f.read()
    CLUB_AND_COLLEGE = eval(content)

#Separate the clubs and universities
CITY_COLLEGE = {}
CITY_CLUBS = {}
for CITILIST, YEARLIST in CLUB_AND_COLLEGE.items():
    CITY_COLLEGE[CITILIST] = {}
    CITY_CLUBS[CITILIST] = {}
    for YEAR, CLUBLIST in CLUB_AND_COLLEGE[CITILIST].items():
        CITY_COLLEGE[CITILIST][YEAR] = {}
        CITY_CLUBS[CITILIST][YEAR] = {}
    for YEAR, CLUBLIST in CLUB_AND_COLLEGE[CITILIST].items():
        for key, value in CLUB_AND_COLLEGE[CITILIST][YEAR].items():
            if "Graduate" in value:
                cleaned_key = key.replace("'", "")
                CITY_COLLEGE[CITILIST][YEAR][cleaned_key] = value
            else:
                CITY_CLUBS[CITILIST][YEAR][key] = value

#Import the dictionary that skip the club pages
with open("city_clubs_page.txt", 'r') as f:
    content = f.read()
    CLUB_PAGE = eval(content)

# In[6]:


# Clean the blank lines
def clean_blank(lines: list):
    output = []
    # Delete the empty lines, and the blanks
    for line in lines:
        if line != "\n" and line != "+\n":
            output.append(line)
    for i in range(len(output)):
        if re.search("\n", output[i]) is not None:
            output[i] = re.sub("\n", ' ', output[i])
    return output

def concat_name_household(outputleft:list):
    i = 0
    while i < len(outputleft) - 1:
        if i < len(outputleft) - 3 and len(outputleft[i].split()) == 1 and re.search(lastname_pattern,outputleft[i]) is not None\
        and len(outputleft[i + 1].split()) == 1 and re.search(lastname_pattern,outputleft[i + 1]) is not None\
        and len(outputleft[i + 2].split()) > 1 and len(outputleft[i + 3].split()) > 1:
            outputleft[i] = outputleft[i] + ' ' + outputleft[i + 2]
            outputleft[i + 1] = outputleft[i + 1] + ' ' + outputleft[i + 3]
            outputleft.pop(i + 3)
            outputleft.pop(i + 2)
        elif len(outputleft[i].split()) == 1 and re.search(lastname_pattern,outputleft[i]) is not None\
        and len(outputleft[i + 1].split()) > 1:
            outputleft[i] = outputleft[i] + ' ' + outputleft[i + 1]
            outputleft.pop(i + 1)
        else:
            i += 1
    return outputleft

def concat_lines(outputleft: list):
    # print(outputleft,len(outputleft))
    # Concact the information in the bracket of the next line into this line
    if len(outputleft) != 0:
        i = 0
        while i < len(outputleft) - 1:
            if re.search(r"\[(.*)", outputleft[i]) is None and re.search(r"\[(.*)", outputleft[i + 1]) is not None:
                bracket = re.search(r"\[(.*)", outputleft[i + 1]).group(1)
                outputleft[i] = outputleft[i] + ' ' + bracket
                try:
                    outputleft[i + 1] = re.sub(re.escape(bracket), "", outputleft[i + 1])
                    outputleft[i + 1] = re.sub(r'\[', "", outputleft[i + 1])
                except:
                    pass
            i += 1

    # Concating the lines connected by a hyphen
    for line in range(len(outputleft)):
        try:
            if outputleft[line][-1] == "-" and re.search(r"^[A-Za-z]", outputleft[line + 1]) is not None:
                outputleft[line] = re.sub(r"(\-$)", "", outputleft[line]) + outputleft[line + 1]
                outputleft.pop(line+1)
        except:
            pass
        try:
            if outputleft[line][0] == "-":
                outputleft[line - 1] = outputleft[line - 1] + re.sub(r"(\-$)", "", outputleft[line])
                outputleft.pop(line)
        except:
            pass
        try:
            if outputleft[line][-1] == "&" and re.search(r"^[A-Za-z]", outputleft[line + 1]) is not None:
                outputleft[line] = outputleft[line] + " " + outputleft[line + 1]
                outputleft.pop(line+1)
        except:
            pass
        try:
            if outputleft[line][0] == "&" :
                outputleft[line - 1] = outputleft[line - 1] + ' ' + outputleft[line]
                outputleft.pop(line)
        except:
            pass

    #Concat the splitted parenthesis (only for household head)
    if len(outputleft) != 0:
        i = 0
        while i < len(outputleft):
            if i + 1 < len(outputleft) and re.search(EXTREME_TITLE_DETECTION, outputleft[i]) is not None\
            and re.search(r"\(",outputleft[i]) is not None and re.search(r"\)", outputleft[i]) is None\
            and re.search(r"\(", outputleft[i + 1]) is None and re.search(r"\)",outputleft[i + 1]) is not None:
                outputleft[i] = outputleft[i] + ' ' + outputleft[i + 1]
                outputleft.pop(i + 1)
            elif i + 2 < len(outputleft) and re.search(EXTREME_TITLE_DETECTION, outputleft[i]) is not None\
            and re.search(r"\(",outputleft[i]) is not None and re.search(r"\)", outputleft[i]) is None\
            and re.search(r"\(", outputleft[i + 2]) is None and re.search(r"\)",outputleft[i + 2]) is not None:
                outputleft[i] = outputleft[i] + ' ' + outputleft[i + 2]
                outputleft.pop(i + 2)
            else:
                i += 1

    #Concat the club lines
    i = 0
    while i < len(outputleft):
        #if i + 3 < len(outputleft) and (re.search(EXTREME_TITLE_DETECTION, outputleft[i]) is not None or re.search(OTHER_DETECTION,outputleft[i]) is not None
        #        or re.search(NOTITLE_DETECTION,outputleft[i]) is not None or re.search(JUNIOR_DETECTION,outputleft[i]) is not None)\
        #        and re.search(LINE_AFTER_PREV, outputleft[i + 1]) is None \
        #        and (re.search(EXTREME_TITLE_DETECTION, outputleft[i + 1]) is not None or re.search(OTHER_DETECTION,outputleft[i + 1]) is not None
        #        or re.search(NOTITLE_DETECTION,outputleft[i + 1]) is not None or re.search(JUNIOR_DETECTION,outputleft[i + 1]) is not None) \
        #        and re.search(LINE_AFTER_PREV, outputleft[i + 2]) is not None \
        #        and re.search(LINE_AFTER_PREV, outputleft[i + 3]) is not None:
        #    outputleft[i] = outputleft[i] + ' ' + outputleft[i + 2]
        #    outputleft.pop(i + 2)

        if i + 1 < len(outputleft) and (re.search(EXTREME_TITLE_DETECTION, outputleft[i]) is not None or
                re.search(NOTITLE_DETECTION,outputleft[i]) is not None or
                re.search(OTHER_DETECTION,add_space_other(outputleft[i])) is not None or
                re.search(JUNIOR_DETECTION, add_space_junior(outputleft[i])) is not None)\
                and re.search(LINE_AFTER_PREV, outputleft[i + 1]) is not None\
                and re.search(EXTREME_TITLE_DETECTION, outputleft[i + 1]) is None\
                and re.search(NOTITLE_DETECTION,outputleft[i + 1]) is None\
                and re.search(OTHER_DETECTION,add_space_other(outputleft[i + 1])) is None\
                and re.search(JUNIOR_DETECTION, add_space_junior(outputleft[i + 1])) is None:
            outputleft[i] = outputleft[i] + ' ' + outputleft[i + 1]
            outputleft.pop(i + 1)
            #print("case1",outputleft[i])
        elif i + 1 < len(outputleft) and (re.search(EXTREME_TITLE_DETECTION, outputleft[i]) is not None or
                re.search(NOTITLE_DETECTION,outputleft[i]) is not None or
                re.search(OTHER_DETECTION,add_space_other(outputleft[i])) is not None or
                re.search(JUNIOR_DETECTION, add_space_junior(outputleft[i])) is not None)\
                and re.search(EXTREME_TITLE_DETECTION,outputleft[i + 1]) is None \
                and re.search(NOTITLE_DETECTION,  outputleft[i + 1]) is None \
                and re.search(OTHER_DETECTION, add_space_other(outputleft[i + 1])) is None \
                and re.search(JUNIOR_DETECTION, add_space_junior(outputleft[i + 1])) is None:
            outputleft[i] = outputleft[i] + ' ' + outputleft[i + 1]
            outputleft.pop(i + 1)
            #print("case2", outputleft[i])
        else:
            i += 1

    # print(outputleft, len(outputleft))
    return outputleft

# First step cleaning for the lines. In order not to break the titles, focus on separating the blocks of \
# first name, middle names and last name, and spouse name
def general_cleaner(input: list):
    for line in range(len(input)):
        # Cleaning
        input[line] = input[line].strip()
        if "Public Domain, Google-digitized" in input[line] \
        or "Generated at Harvard University" in input[line] \
        or 'Digitized' in input[line]:
            input[line] = ''
        if "â€™" in input[line]:
            input[line] = input[line].replace("â€™", "'")
        if "\\" in input[line]:
            input[line] = input[line].replace("\\", "")
        if "Ã©" in input[line]:
            input[line] = input[line].replace("Ã©", "é")

        for key in CORRECT_LETTERS:
            for WRONG_LETTER in CORRECT_LETTERS[key]:
                if WRONG_LETTER in input[line]:
                    input[line] = re.sub(WRONG_LETTER, key, input[line])

        # Spacing
        # Separate the last name and the titles; Avoid splitting some last names like 'LaFarge'
        if re.search(r"^[A-Z][a-z][A-Z][a-z]", input[line]) is None:
            try:
                input[line] = re.sub(r"^([A-Z][a-z]+)([A-Z])", r"\1 \2", input[line])
            except:
                pass
        else:
            try:
                input[line] = re.sub(r"^([A-Z][a-z][a-z]?[A-Z][a-z]+)([A-Z])", r"\1 \2", input[line])
            except:
                pass

        # Separate the first name and middle names after the title, before the spouse
        try:
            # ?<=: positive lookbehind, check appear before
            # ?<!: negative lookbehind, check not appear before
            input[line] = re.sub(r"((?<=\S)(?<!\()(?<!\&)[A-Z][a-z]+(?!\')(?!\"))", r" \1", input[line])
        except:
            pass



    for k in range(len(input)):
        if re.search(PARENTHESES_BEFORE_STRING, input[k]) is not None:
            input[k] = re.sub(r"\)", ") ", input[k])
        if re.search(PARENTHESES_AFTER_STRING, input[k]) is not None:
            input[k] = re.sub(r"\(", " (", input[k])
        if re.search(SPACING_OF_HYPHENS, input[k]) is not None:
            input[k] = re.sub(r"\-", " - ", input[k])
        if re.search(TITLE_FIX_END_OF_PREV, input[k]) is not None:
            match_part = re.search(TITLE_FIX_END_OF_PREV, input[k]).group(1)
            input[k] = re.sub(f"{match_part}", f"{match_part} ", input[k])
        #Cleaning for quotation mark (the apostrophe is actually read as quotation marks)
        #First try to space out the titles, and conncect the normal names
        #Do not clean the space for ", which could be titles sometimes
        #Do not clean the space for all ' (only those following specific letters), which could appear in Dutch or other lastnames
        input[k] = re.sub(r"[a-jhp-uzMNID](\")([A-Z])", r"\1 \2", input[k])
        input[k] = re.sub(r"[a-jhp-uzMNID](\')([A-Z])", r"\1 \2", input[k])
        input[k] = re.sub(r"(\') ([a-z])", r"\1\2", input[k])
        input[k] = re.sub(r"([A-Za-z]) (\')", r"\1\2", input[k])
        #Try to separate the "&" except for those precede titles(WDnlrjetNM) and after titles(MNC)
        input[k] = re.sub(r"(&)([A-BD-LO-Z])", r"\1 \2", input[k])
        input[k] = re.sub(r"[A-CKO-PQ-Za-ikm-qs-z](&)([A-Z])", r"\1 \2", input[k])
        input[k] = re.sub(r"([A-CKO-PQ-Za-ikm-qs-z])(&)", r"\1 \2", input[k])
        input[k] = re.sub(r"([A-Za-z])(&)[A-BD-LO-Z]", r"\1 \2", input[k])
        input[k] = re.sub(r"(\.)(&)", r"\1 \2", input[k])
    return input


def correct_title(to_be_cleaned: str):
    to_be_cleaned = to_be_cleaned.strip()
    for key in CORRECT_TITLES:
        for WRONG_TITLE in CORRECT_TITLES[key]:
            if to_be_cleaned == WRONG_TITLE:
                to_be_cleaned = key

    return to_be_cleaned


# Second step cleaning for the names.
def add_spaces(to_be_cleaned: str, type: str):
    # add space between two upper case letter in the same string
    _ = re.sub(r"([A-Z])([A-Z])", r"\1 \2", to_be_cleaned)
    # add space between a lower case letter and upper case letter in the same string
    __ = re.sub(r"\b([A-z]?[a-z])([A-Z])", r"\1 \2", _)
    # eliminate space before and after apostrophe
    ___ = re.sub(r"(\') ([a-z])", r"\1\2", __)
    # clean the asterisk in the names
    ___ = re.sub(r"\*", " ", ___)
    ___ = re.sub(r"\(", "", ___)
    ___ = re.sub(r"\)", "", ___)

    # split the words into a list by spaces
    output = ___.split(" ")
    # Adjust to full name
    for i in range(len(output)):
        for key in NAME_ABBRV:
            if output[i] == key:
                output[i] = NAME_ABBRV[key]

    if type == "STRING":
        out = " ".join(output).strip()
    elif type == "LIST":
        out = list(output)
        out = [item.strip() for item in out if item.strip()]
    return out

# Add extra space for juniors detection
def add_space_junior(to_be_cleaned: str):
    # add space between a letter and non-letter characteristic
    to_be_cleaned = to_be_cleaned.strip()
    __ = re.sub(r"([A-Z][a-z]*)(?! )(&)", r"\1 \2", to_be_cleaned)
    ___ = re.sub(r"(&)(?! )([A-Z][a-z]*)", r"\1 \2", __)
    ___ = re.sub(r"^(J)(M)", r"\1 \2", ___)
    ___ = re.sub(r"^(J)(N)", r"\1 \2", ___)
    ___ = re.sub(r"^(J')([A-Z])", r"\1 \2", ___)
    output = ___.split(" ")

    return " ".join(output).strip()

# Add extra space for others detection
def add_space_other(to_be_cleaned: str):
    # add space between a letter and non-letter characteristic
    to_be_cleaned = to_be_cleaned.strip()
    __ = re.sub(r"([A-Z][a-z]*)(?<![MNWDCtrs])(?<!Lt)(?<!Gen)(?<!Maj)(?<!Capt)(?<!Col)(?<!LtCol)(?! )(&)", r"\1 \2", to_be_cleaned)
    ___ = re.sub(r"(&)(?! )(?![MNEWTCtrs\"\'\*]+)([A-Z][a-z]*)", r"\1 \2", __)
    output = ___.split(" ")

    return " ".join(output).strip()

# Generate the address
def get_address(outputright: list):
    # print(outputright)
    address = ""
    for i in range(len(outputright)):
        address = address + outputright[i]

    return address


def clean_address(outputright: list):
    # print(outputright)
    address = ""
    for i in range(len(outputright)):
        if re.search(PHONE, outputright[i]) is None and re.search(OTHER, outputright[i]) is None\
        and re.search(PHONE2,outputright[i]) is None and re.search(PHONE3, outputright[i]) is None\
        and re.search(PHONE4, outputright[i]) is None:
            address = address + outputright[i]
    # print(address)

    for key in CORRECT_ADDRESS:
        for WRONG_ADDRESS in CORRECT_ADDRESS[key]:
            if re.search(WRONG_ADDRESS, address) is not None:
                address = re.sub(WRONG_ADDRESS, key, address)

    address = re.sub(TRIVIAL, '', address)
    address = re.sub(ELSE, '', address)
    address = re.sub(TIME, '', address)
    address = re.sub(r"([A-Z])([A-Z])", r"\1 \2", address)
    address = re.sub(r"([A-z]?[a-z]{1,})([A-Z])", r"\1 \2", address)
    address = re.sub(r"([A-Za-z]+)([0-9]+)", r"\1 \2", address)
    address = re.sub(r"([0-9]+)([A-Za-z]+)", r"\1 \2", address)
    address = re.sub(OTHER, '', address)
    address = re.sub(OTHER2, '', address)
    # print(address)

    if re.search(ELSE, address) is not None:
        address = ""
    elif address.isspace():
        address = ""
    return address.strip()

def get_firstmiddle(first_and_middle_name: str):
    first_name = 'None'
    middle_name = 'None'
    first_and_middle_name = add_spaces(first_and_middle_name,"LIST")
    if first_and_middle_name[-1] in suffix:
        suffix_name = first_and_middle_name[-1]
        first_and_middle_name = first_and_middle_name[:-1]
    else:
        suffix_name = 'None'

    if len(first_and_middle_name) == 1:
        middle_name = 'None'
        first_name = first_and_middle_name[0]
    elif len(first_and_middle_name) > 1:
        first_name = first_and_middle_name[0]
        middle_name = ' '.join(first_and_middle_name[1:])
        # Just preserve the position of the name as where it is!
        #if len(first_and_middle_name[0]) == 1:
            #The range(num) start from 0 to num-1
        #    for m in range(len(first_and_middle_name[1:])+1):
        #        if len(first_and_middle_name[m]) > 1:
        #            first_name = first_and_middle_name[m]
        #            middle_name = ' '.join(first_and_middle_name[:m] + first_and_middle_name[m + 1:])
        #            break
    return first_name, middle_name, suffix_name

def get_fullname(full_name: str):
    first_name = 'None'
    middle_name = 'None'
    last_name = 'None'
    suffix_name = 'None'
    full_name = add_spaces(full_name,"LIST")
    if full_name[-1] in suffix:
        suffix_name = full_name[-1]
        full_name = full_name[:-1]
    else:
        suffix_name = 'None'

    if len(full_name) == 1:
        last_name = full_name[0]
        first_name = 'None'
        middle_name = 'None'
    elif len(full_name) == 2:
        if full_name[-2] in surname:
            first_name = 'None'
            last_name = ' '.join(full_name[-2:])
            middle_name = 'None'
        else:
            first_name = full_name[0]
            last_name = full_name[-1]
            middle_name = 'None'
    elif len(full_name) > 2:
        if full_name[-2] in surname:
            first_name = full_name[0]
            last_name = ' '.join(full_name[-2:])
            middle_name = ' '.join(full_name[1:-2])
            #if len(full_name[0]) == 1:
            #    for m in range(len(full_name[:-2])+1):
            #        if len(full_name[m]) > 1:
            #            first_name = full_name[m]
            #            middle_name = ' '.join(full_name[:m] + full_name[m + 1:-2])
            #            break
        else:
            first_name = full_name[0]
            last_name = full_name[-1]
            middle_name = ' '.join(full_name[1:-1])
            #if len(full_name[0]) == 1:
            #    for m in range(len(full_name[:-1])+1):
            #        if len(full_name[m]) > 1:
            #            first_name = full_name[m]
            #            middle_name = ' '.join(full_name[:m] + full_name[m + 1:-1])
            #            break
    return first_name, middle_name, last_name, suffix_name

def get_notitlename(full_name: str):
    first_name = 'None'
    middle_name = 'None'
    last_name = 'None'
    suffix_name = 'None'
    full_name = add_spaces(full_name,"LIST")

    if full_name[-1] in suffix:
        suffix_name = full_name[-1]
        full_name = full_name[:-1]
    else:
        suffix_name = 'None'

    if len(full_name) == 2:
        first_name = full_name[1]
        last_name = full_name[0]
        middle_name = 'None'
    elif len(full_name) > 2:
        if full_name[0] in surname:
            last_name = ' '.join(full_name[0:2])
            first_name = full_name[2]
            middle_name = ' '.join(full_name[3:])
            #if len(full_name[2]) == 1:
            #    for m in range(2,len(full_name[2:])+1):
            #        if len(full_name[m]) > 1:
            #            first_name = full_name[m]
            #            middle_name = ' '.join(full_name[2: m] + full_name[m + 1:])
            #            break
        else:
            first_name = full_name[1]
            last_name = full_name[0]
            middle_name = ' '.join(full_name[2:])
            #if len(full_name[1]) == 1:
            #    for m in range(1, len(full_name[1:])+1):
            #        if len(full_name[m]) > 1:
            #            first_name = full_name[m]
            #            middle_name = ' '.join(full_name[1: m] + full_name[m + 1:])
            #            break

    return first_name, middle_name, last_name, suffix_name

def get_spousename(spouse_name: str):
    first = 'None'
    middle = 'None'
    last = 'None'
    spouse_surname = 'None'
    if spouse_name is not None:
        spouse_name = spouse_name.strip()
        if spouse_name is not None and not spouse_name.isspace():
            spouse_fullname = spouse_name.split("-")
            if len(spouse_fullname) == 1:
                spouse_name = add_spaces(spouse_fullname[0], "LIST")
                spouse_surname = 'None'
            else:
                spouse_name = add_spaces(spouse_fullname[-1], "LIST")
                spouse_surname = "-".join(spouse_fullname[0:-1]).strip()

            if spouse_name is not None:
                if len(spouse_name) == 1:
                    first = 'None'
                    middle = 'None'
                    last = spouse_name[0]
                elif len(spouse_name) == 2:
                    if spouse_name[-2] in surname:
                        first = 'None'
                        last = ' '.join(spouse_name[-2:])
                        middle = 'None'
                    else:
                        first = spouse_name[0]
                        last = spouse_name[1]
                        middle = 'None'
                elif len(spouse_name) > 2:
                    if spouse_name[-2] in surname:
                        first = spouse_name[0]
                        last = ' '.join(spouse_name[-2:])
                        middle = ' '.join(spouse_name[1:-2])
                        #if len(spouse_name[0]) == 1:
                        #    for m in range(len(spouse_name[:-2])+1):
                        #        if len(spouse_name[m]) > 1:
                        #            first = spouse_name[m]
                        #            middle = ' '.join(spouse_name[:m] + spouse_name[m + 1:-2])
                        #            break
                    else:
                        last = spouse_name[-1]
                        first = spouse_name[0]
                        middle = ' '.join(spouse_name[1:-1])
                        #if len(spouse_name[0]) == 1:
                        #    for m in range(len(spouse_name[:-1])+1):
                        #        if len(spouse_name[m]) > 1:
                        #            first = spouse_name[m]
                        #            middle = ' '.join(spouse_name[:m] + spouse_name[m + 1:-1])
                        #            break

            else:
                first = 'None'
                middle = 'None'
                last = 'None'
        else:
            first = 'None'
            middle = 'None'
            last = 'None'
    else:
        first = 'None'
        middle = 'None'
        last = 'None'

    return first, middle, last, spouse_surname

def get_club(clublines:str):
    global city
    global year
    gradyear = ''
    gradyearlist = []
    college_complete = []
    clubs_complete = []
    clubs = []
    for YEAR, CLUBLIST in CLUB_AND_COLLEGE[city].items():
        min = re.search(r'(\d{4})', YEAR).group(1)
        max = re.search(r'(\d{4})$', YEAR).group(1)
        if  int(year) >= int(min) and int(year) <=int(max):
            year_range = YEAR

    keyforclubs = list(CITY_CLUBS[city][year_range].keys())
    keyforcolleges = list(CITY_COLLEGE[city][year_range].keys())
    for j in keyforclubs:
        if "," in j:
            j = j.replace(",", ".")
        club_full = re.findall(r"" + j + "(?=\.)", clublines)
        if len(club_full) > 0:
            clubs.append(club_full[0])
            try:
                clubs_complete.append(CITY_CLUBS[city][year_range][j])
            except:
                pass

    if len(clubs) > 0:
        clubs_raw = ', '.join(clubs)
    else:
        clubs_raw = ''
    if len(clubs_complete) > 0:
        clubs_clean = ', '.join(clubs_complete)
    else:
        clubs_clean = ''

    for j in keyforcolleges:
        if "," in j:
            j = j.replace(",", ".")
        college_full = re.findall(r"(" + j + "\'[0-9o][0-9o]|" + j + "\.\'[0-9o][0-9o])", clublines)

        if len(college_full) > 0:
            uni = j
            grad_year_base = re.search(r"(((?<=" + j + "\')[0-9o][0-9o])|((?<=" + j + "\.\')[0-9o][0-9o]))",clublines).group(1).strip()
            if "o" in grad_year_base:
                grad_year_base = grad_year_base.replace("o", "0")
            if 1900 + int(grad_year_base) > int(year):
                gradyear = str(1800 + int(grad_year_base))
                gradyearlist.append(gradyear)
            else:
                gradyear = str(1900 + int(grad_year_base))
                gradyearlist.append(gradyear)
            try:
                univer = CITY_COLLEGE[city][year_range][uni]
                college_complete.append(str(univer + ' ' + gradyear))
            except:
                pass

    if len(college_complete) > 0:
        college =', '.join(college_complete)
        grad_year = ', '.join(gradyearlist)
    else:
        college = ''
        grad_year = ''

    return clubs_raw, clubs_clean, grad_year, college

# Create the result for multiple lines of family
def generate_result(outputleft: list, outputright: list):
    global household
    global marriage
    household_last_name = None

    #print("A", len(outputleft), outputleft)

    # left = outputleft[:]
    # r1 = [left,len(left)]
    # Clean the lines
    if len(outputleft) != 0 and len(outputright) != 0:
        #Concatthe club lines
        k = 0
        while k < len(outputleft) - 1:
            if re.search(EXTREME_TITLE_DETECTION, outputleft[k + 1]) is None\
            and re.search(OTHER_DETECTION,add_space_other(outputleft[k + 1])) is None\
            and re.search(JUNIOR_DETECTION, add_space_junior(outputleft[k + 1])) is None\
            and re.search(NOTITLE_DETECTION, outputleft[k + 1]) is None\
            and (re.search(r"[A-Z][a-z]?[a-z]?\.", outputleft[k + 1]) is not None\
                 or re.search(r"[A-Z][a-z]?[a-z]?\'", outputleft[k + 1]) is not None):
                outputleft[k] = outputleft[k] + ' ' + outputleft[k + 1]
                outputleft.pop(k + 1)
            else:
                k += 1

        k = 0
        while k < len(outputleft):
            if re.search(EXTREME_TITLE_DETECTION, outputleft[k]) is None\
                and re.search(OTHER_DETECTION,add_space_other(outputleft[k])) is None\
                and re.search(JUNIOR_DETECTION, add_space_junior(outputleft[k])) is None\
                and re.search(NOTITLE_DETECTION,outputleft[k]) is None:
                outputleft.pop(k)
            else:
                k += 1

        #Clean the families do not start with the hosuehold head
        if len(outputleft) > 0 and re.search(JUNIOR_DETECTION, add_space_junior(outputleft[0])) is not None:
            outputleft.clear()
        if len(outputleft) > 0 and re.search(EXTREME_TITLE_DETECTION, outputleft[0]) is None\
        and re.search(OTHER_DETECTION, add_space_other(outputleft[0])) is not None:
            outputleft.clear()
        # r2 = [outputleft,len(outputleft)]
        # if r1[1] != r2[1]:
        #    print(r1,r2)
        #print("D",len(outputleft),outputleft)

    if len(outputleft) != 0 and len(outputright) != 0:
        # print(len(outputleft),outputleft)
        # Update household ID
        # if len(outputleft) > 1:
        #    household += 1
        # elif len(outputleft) == 1 and re.search("\(.+\)", outputleft[0]) is not None:
        household += 1
        blended_family = 0
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
            # fullname = re.findall(EXTREME_TITLE_DETECTION, outputleft[k])
            # print(fullname)
            other_name = re.search(OTHER_DETECTION, add_space_other(outputleft[k]))
            multiple_name = re.search(MULTIPLE_DETECTION, add_space_other(outputleft[k]))
            other_junior_name = re.search(OTHER_JUNIOR_DETECTION, add_space_other(outputleft[k]))
            # print(full_name,junior_name,other_name)
            notitle_name = re.search(NOTITLE_DETECTION, outputleft[k])

            col_marriage.append('0')

            if re.search("Died", outputleft[k]) is not None or re.search("Died", get_address(outputright)) is not None:
                die = 1
            else:
                die = 0
            died.append(die)
            # print(die)
            # print(len(died))

            col_city.append(city)
            col_year.append(year)
            col_household.append(household)
            addr_origin = clean_address(outputright)
            if re.search(MOVE, addr_origin) is not None:
                addr = re.sub(MOVE, '', addr_origin)
                move = re.search(MOVE, addr_origin).group(2)
                col_address.append(addr)
                newregister.append(move)
            else:
                col_address.append(addr_origin)
                newregister.append('')

            try:
                foreign.append(re.search(FOREIGN, outputright).group(0).strip())
            except:
                foreign.append("No")
            # print(outputright)
            # print(clean_address(outputright))
            # print(col_city,col_year,col_address)
            # print(len(col_city),len(col_year),len(col_address))

            if k == 0 and len(outputleft) > 1:
                col_hhhead.append('1')
                if re.search(EXTREME_TITLE_DETECTION, outputleft[k]) is not None:
                    household_last_name = add_spaces(full_name.group(1), "STRING")
                    if full_name.group(12) is not None:
                        if re.search("\-", full_name.group(12)) is not None:
                            blended_family = 1
                            previous_last_name = re.search("(.*)\-(.*)",full_name.group(12)).group(1)
                elif re.search(NOTITLE_DETECTION, outputleft[k]) is not None:
                    household_last_name = add_spaces(notitle_name.group(1), "STRING")
                    if notitle_name.group(9) is not None:
                        if re.search("\-", notitle_name.group(9)) is not None:
                            blended_family = 1
                            previous_last_name = re.search("(.*)\-(.*)", notitle_name.group(9)).group(1)
            elif k == 0 and re.search("\(.+\)", outputleft[0]) is not None and len(outputleft) == 1:
                col_hhhead.append('1')
            elif k == 0 and re.search("\(.+\)", outputleft[0]) is None and len(outputleft) == 1:
                col_hhhead.append('0')
            elif k > 0 and junior_name is not None:
                col_hhhead.append('3')
            elif k > 0 and full_name is None and other_name is not None:
                col_hhhead.append('5')
            else:
                col_hhhead.append('4')
            # print(col_hhhead)
            # print(len(col_hhhead))

            if junior_name is not None:
                #print(k,"case1", junior_name)
                #juniorname = re.findall(JUNIOR_DETECTION,outputleft[k])
                #print(juniorname)
                junior_number = outputleft[k].count('&') + 1
                for i in range(junior_number): #starting from 0 to num-1
                    if 9*(i+1) <= len(junior_name.groups()) and junior_name.group(9*i+4) is not None\
                    and not junior_name.group(9*i+4).isspace():
                        if i == 0:
                            col_spousename.append('None')
                            col_spouselast.append('None')
                            col_spousemiddle.append('None')
                            col_spouselastsurname.append('None')
                        elif i > 0:
                            col_household.append(col_household[-1])
                            col_hhhead.append(col_hhhead[-1])
                            col_city.append(col_city[-1])
                            col_year.append(col_year[-1])
                            col_address.append(col_address[-1])
                            newregister.append(newregister[-1])
                            col_spousename.append('None')
                            col_spouselast.append('None')
                            col_spousemiddle.append('None')
                            col_spouselastsurname.append('None')
                            col_marriage.append("0")
                            foreign.append(foreign[-1])
                            died.append('0')

                        if junior_name.group(9*i+3) is not None:
                            col_title.append(correct_title(junior_name.group(9*i+3)))
                        elif i == 0 and junior_name.group(9*i+3) is None:
                            col_title.append('')
                        elif i > 0 and 9*(i+1) <= len(junior_name.groups())\
                        and junior_name.group(9*i+3) is None and junior_name.group(9*(i-1)+3) is not None:
                            col_title.append(correct_title(junior_name.group(9*(i-1)+3)))
                        elif i > 1 and 9*(i+1) <= len(junior_name.groups())\
                        and junior_name.group(9*i+3) is None and junior_name.group(9*(i-1)+3) is None\
                        and junior_name.group(9*(i-2)+3) is not None:
                            col_title.append(correct_title(junior_name.group(9*(i-2)+3)))
                        else:
                            col_title.append('')

                        if junior_name.group(9*i+9) is not None:
                            raw, clean, grad, colle = get_club(junior_name.group(9*i+9))
                            clubs_raw.append(raw)
                            clubs_clean.append(clean)
                            grad_year.append(grad)
                            college.append(colle)
                        else:
                            clubs_raw.append('')
                            clubs_clean.append('')
                            grad_year.append('')
                            college.append('')

                        if blended_family == 0:
                            if household_last_name is not None:
                                col_lastname.append(household_last_name)
                            else:
                                col_lastname.append('Junior')

                            first_name, middle_name, suffix_name = get_firstmiddle(junior_name.group(9*i+4))
                            col_firstname.append(first_name)
                            col_middlename.append(middle_name)
                            col_suffix.append(suffix_name)
                        elif blended_family == 1:
                            if re.search(previous_last_name,junior_name.group(9*i+4)) is not None:
                                first_name, middle_name, last_name, suffix_name = get_fullname(junior_name.group(9*i+4))
                            else:
                                last_name = household_last_name
                                first_name, middle_name, suffix_name = get_firstmiddle(junior_name.group(9*i+4))

                            col_firstname.append(first_name)
                            col_middlename.append(middle_name)
                            col_lastname.append(last_name)
                            col_suffix.append(suffix_name)

            elif other_junior_name is not None:
                #print(re.findall(OTHER_JUNIOR_DETECTION,outputleft[k]))
                col_lastname.extend([other_junior_name.group(1)] * 2)
                col_title.append(other_junior_name.group(2))
                col_title.append(other_junior_name.group(13))

                first_name1, middle_name1, suffix_name1 = get_firstmiddle(other_junior_name.group(3))
                first_name2, middle_name2, suffix_name2 = get_firstmiddle(other_junior_name.group(14))
                col_firstname.append(first_name1)
                col_middlename.append(middle_name1)
                col_suffix.append(suffix_name1)
                col_firstname.append(first_name2)
                col_middlename.append(middle_name2)
                col_suffix.append(suffix_name2)

                if other_junior_name.group(11) is not None:
                    raw, clean, grad, colle = get_club(other_junior_name.group(11))
                    clubs_raw.append(raw)
                    clubs_clean.append(clean)
                    grad_year.append(grad)
                    college.append(colle)
                else:
                    clubs_raw.append('')
                    clubs_clean.append('')
                    grad_year.append('')
                    college.append('')

                if other_junior_name.group(19) is not None:
                    raw, clean, grad, colle = get_club(other_junior_name.group(19))
                    clubs_raw.append(raw)
                    clubs_clean.append(clean)
                    grad_year.append(grad)
                    college.append(colle)
                else:
                    clubs_raw.append('')
                    clubs_clean.append('')
                    grad_year.append('')
                    college.append('')

                col_spousename.extend(['None'] * 2)
                col_spouselast.extend(['None'] * 2)
                col_spousemiddle.extend(['None'] * 2)
                col_spouselastsurname.extend(['None'] * 2)
                col_household.append(col_household[-1])
                col_hhhead.append(col_hhhead[-1])
                col_city.append(col_city[-1])
                col_year.append(col_year[-1])
                col_address.append(col_address[-1])
                newregister.append(newregister[-1])
                foreign.append(foreign[-1])
                col_marriage.append("0")
                died.append('0')

            elif other_name is not None:
                #print(k, "case2", other_name)
                #othername = re.findall(OTHER_DETECTION, add_space_junior(outputleft[k]))
                #print(city + year, k, 'case4', othername)
                if 36 <= len(other_name.groups()) and other_name.group(28) is not None \
                and not other_name.group(28).isspace():
                    first_name3, middle_name3, last_name, suffix_name3 = get_fullname(other_name.group(29))
                    first_name2, middle_name2, suffix_name2 = get_firstmiddle(other_name.group(17))
                    first_name1, middle_name1, suffix_name1 = get_firstmiddle(other_name.group(5))
                    col_firstname.append(first_name1)
                    col_middlename.append(middle_name1)
                    col_lastname.append(last_name)
                    col_suffix.append(suffix_name1)
                    col_firstname.append(first_name2)
                    col_middlename.append(middle_name2)
                    col_lastname.append(last_name)
                    col_suffix.append(suffix_name2)
                    col_firstname.append(first_name3)
                    col_middlename.append(middle_name3)
                    col_lastname.append(last_name)
                    col_suffix.append(suffix_name3)

                elif 24 <= len(other_name.groups()) and other_name.group(16) is not None \
                and not other_name.group(16).isspace():
                    first_name2, middle_name2, last_name, suffix_name2 = get_fullname(other_name.group(17))
                    first_name1, middle_name1, suffix_name1 = get_firstmiddle(other_name.group(5))
                    col_firstname.append(first_name1)
                    col_middlename.append(middle_name1)
                    col_lastname.append(last_name)
                    col_suffix.append(suffix_name1)
                    col_firstname.append(first_name2)
                    col_middlename.append(middle_name2)
                    col_lastname.append(last_name)
                    col_suffix.append(suffix_name2)

                elif 12 <= len(other_name.groups()) and other_name.group(4) is not None\
                and not other_name.group(4).isspace():
                    first_name, middle_name, last_name, suffix_name = get_fullname(other_name.group(5))
                    col_firstname.append(first_name)
                    col_middlename.append(middle_name)
                    col_lastname.append(last_name)
                    col_suffix.append(suffix_name)

                for i in range(3):  # starting from 0;
                    if 12*i <= len(other_name.groups()) and other_name.group(12*i+4) is not None \
                    and not other_name.group(12*i+4).isspace():
                        spouse_first, spouse_middle, spouse_last, spouse_lastsurname = get_spousename(other_name.group(12*i+10))
                        col_spousename.append(spouse_first)
                        col_spouselast.append(spouse_last)
                        col_spousemiddle.append(spouse_middle)
                        col_spouselastsurname.append(spouse_lastsurname)
                        if other_name.group(12*i+3) is not None:
                            col_title.append(correct_title(other_name.group(12*i+3)))
                        elif i == 0 and other_name.group(12*i+3) is None:
                            col_title.append('')
                        elif i > 0 and 12*(i+1) <= len(other_name.groups()) \
                                and other_name.group(12*i+3) is None and other_name.group(12*(i-1)+3) is not None:
                            col_title.append(correct_title(other_name.group(12*(i-1)+3)))
                        elif i > 1 and 12*(i+1) <= len(other_name.groups()) \
                                and other_name.group(12*i+3) is None and other_name.group(12*(i-1)+3) is None \
                                and other_name.group(12*(i-2)+3) is not None:
                            col_title.append(correct_title(other_name.group(12*(i-2)+3)))
                        else:
                            col_title.append('')
                        if other_name.group(12*i+12) is not None:
                            raw, clean, grad, colle = get_club(other_name.group(12*i+12))
                            clubs_raw.append(raw)
                            clubs_clean.append(clean)
                            grad_year.append(grad)
                            college.append(colle)
                        else:
                            clubs_raw.append('')
                            clubs_clean.append('')
                            grad_year.append('')
                            college.append('')
                        if i > 0:
                            col_household.append(col_household[-1])
                            col_hhhead.append(col_hhhead[-1])
                            col_city.append(col_city[-1])
                            col_year.append(col_year[-1])
                            col_address.append(col_address[-1])
                            newregister.append(newregister[-1])
                            col_marriage.append("0")
                            foreign.append(foreign[-1])
                            died.append('0')

            elif multiple_name is not None:
                col_lastname.extend([multiple_name.group(1)] * 2)
                col_title.append(multiple_name.group(2))
                col_title.append(multiple_name.group(9))

                first_name1, middle_name1, suffix_name1 = get_firstmiddle(multiple_name.group(3))
                first_name2, middle_name2, suffix_name2 = get_firstmiddle(multiple_name.group(10))
                col_firstname.append(first_name1)
                col_middlename.append(middle_name1)
                col_suffix.append(suffix_name1)
                col_firstname.append(first_name2)
                col_middlename.append(middle_name2)
                col_suffix.append(suffix_name2)

                if multiple_name.group(8) is not None:
                    raw, clean, grad, colle = get_club(multiple_name.group(8))
                    clubs_raw.append(raw)
                    clubs_clean.append(clean)
                    grad_year.append(grad)
                    college.append(colle)
                else:
                    clubs_raw.append('')
                    clubs_clean.append('')
                    grad_year.append('')
                    college.append('')

                if multiple_name.group(15) is not None:
                    raw, clean, grad, colle = get_club(multiple_name.group(15))
                    clubs_raw.append(raw)
                    clubs_clean.append(clean)
                    grad_year.append(grad)
                    college.append(colle)
                else:
                    clubs_raw.append('')
                    clubs_clean.append('')
                    grad_year.append('')
                    college.append('')

                col_spousename.extend(['None'] * 2)
                col_spouselast.extend(['None'] * 2)
                col_spousemiddle.extend(['None'] * 2)
                col_spouselastsurname.extend(['None'] * 2)
                col_household.append(col_household[-1])
                col_hhhead.append(col_hhhead[-1])
                col_city.append(col_city[-1])
                col_year.append(col_year[-1])
                col_address.append(col_address[-1])
                newregister.append(newregister[-1])
                foreign.append(foreign[-1])
                col_marriage.append("0")
                died.append('0')

            elif full_name is not None:
                #print(k,'case3',full_name)
                fullname = re.findall(EXTREME_TITLE_DETECTION,outputleft[k])
                col_lastname.append(full_name.group(1))
                col_title.append(correct_title(full_name.group(2)))
                first_name, middle_name, suffix_name = get_firstmiddle(full_name.group(4))
                col_firstname.append(first_name)
                col_middlename.append(middle_name)
                col_suffix.append(suffix_name)

                spouse_first, spouse_middle, spouse_last, spouse_lastsurname = get_spousename(full_name.group(12))
                col_spousename.append(spouse_first)
                col_spouselast.append(spouse_last)
                col_spousemiddle.append(spouse_middle)
                col_spouselastsurname.append(spouse_lastsurname)

                if full_name.group(13) is not None:
                    raw, clean, grad, colle = get_club(full_name.group(13))
                    clubs_raw.append(raw)
                    clubs_clean.append(clean)
                    grad_year.append(grad)
                    college.append(colle)
                else:
                    clubs_raw.append('')
                    clubs_clean.append('')
                    grad_year.append('')
                    college.append('')

            elif notitle_name is not None:
                #print(k, 'case4', notitle_name)
                # notitlename = re.findall(EXTREME_TITLE_DETECTION,outputleft[k])
                # print(notitlename)
                col_title.append('')
                first_name, middle_name, last_name, suffix_name = get_notitlename(notitle_name.group(1))
                col_firstname.append(first_name)
                col_middlename.append(middle_name)
                col_lastname.append(last_name)
                col_suffix.append(suffix_name)

                spouse_first, spouse_middle, spouse_last,spouse_lastsurname = get_spousename(notitle_name.group(9))
                col_spousename.append(spouse_first)
                col_spouselast.append(spouse_last)
                col_spousemiddle.append(spouse_middle)
                col_spouselastsurname.append(spouse_lastsurname)

                if notitle_name.group(10) is not None:
                    raw, clean, grad, colle = get_club(notitle_name.group(10))
                    clubs_raw.append(raw)
                    clubs_clean.append(clean)
                    grad_year.append(grad)
                    college.append(colle)
                else:
                    clubs_raw.append('')
                    clubs_clean.append('')
                    grad_year.append('')
                    college.append('')



    if any(len(lst) != len(col_city) for lst in
           [col_marriage, col_city, col_year, col_lastname, col_title, col_middlename, col_firstname, col_spousename,
            col_spousemiddle, col_spouselast, col_address, col_household, col_hhhead, clubs_raw, clubs_clean, grad_year,
            foreign, died]):
        print("city:", col_city, "year:", col_year, "household_id:", col_household,
              "household_structure:", col_hhhead,
              "last_name:", col_lastname, "title:", col_title, "first_name:", col_firstname,
              "middle_names:", col_middlename,
              "spouse_name:", col_spousename, "spouse_middle_names:", col_spousemiddle, "spouse_last_name:",
              col_spouselast, "new_marriage:", col_marriage,
              "clubs_abbr:", clubs_raw, "clubs_extended:", clubs_clean, "grad_year:", grad_year,
              "foreign:", foreign, "died:", died, "address:", col_address, "new_register:", newregister)
        print("city:", len(col_city), "year:", len(col_year), "household_id:", len(col_household),
              "household_structure:", len(col_hhhead),
              "last_name:", len(col_lastname), "title:", len(col_title), "first_name:", len(col_firstname),
              "middle_names:", len(col_middlename),
              "spouse_name:", len(col_spousename), "spouse_middle_names:", len(col_spousemiddle), "spouse_last_name:",
              len(col_spouselast), "new_marriage:", len(col_marriage),
              "clubs_abbr:", len(clubs_raw), "clubs_extended:", len(clubs_clean), "grad_year:", len(grad_year),
              "foreign:", len(foreign),
              "died:", len(died), "address:", len(col_address), "new_register:", len(newregister))

    return col_spouselastsurname,col_suffix,col_marriage, newregister, household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address

# In[7]:

def match_family(left: str, right: str):
    lefttxt = open(left, 'r', encoding="UTF-8")
    righttxt = open(right, 'r', encoding="UTF-8")
    leftlines = lefttxt.readlines()
    rightlines = righttxt.readlines()

    #print("A", len(leftlines), leftlines)
    outputleft = clean_blank(leftlines)
    outputright = clean_blank(rightlines)
    outputleft = concat_name_household(outputleft)
    outputleft = concat_lines(outputleft)
    #print("B", len(outputleft), outputleft)
    outputleft = general_cleaner(outputleft)
    outputright = general_cleaner(outputright)
    #print("C", len(outputleft), outputleft)
    col_spouselastsurname,col_suffix, col_marriage, newregister, household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address = generate_result(
        outputleft, outputright)


# In[8]:

# Print the output into a txt file
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
csvpath = workdir + "csv_output\\"
if os.path.exists(csvpath):
    shutil.rmtree(csvpath)
os.makedirs(csvpath)

household_dic = {}

for txtpath, txtdirs, _ in os.walk(workdir + "text_output_household"):
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
        col_marriage = []
        col_spouselastsurname = []
        col_suffix = []
        household = 0
        marriage = 0

        for i in range(1, 500000):
            left_txt = os.path.join(txtpath, city + ' ' + year, "L" + str(i).zfill(5) + ".txt")
            right_txt = os.path.join(txtpath, city + ' ' + year, "R" + str(i).zfill(5) + ".txt")
            empty_txt = os.path.join(txtpath, city + ' ' + year, "empty.txt")
            if os.path.exists(left_txt):
                is_club_page = False
                leftlines = open(left_txt, 'r', encoding="UTF-8").readlines()
                for line in range(len(leftlines)):
                    if "The date following" in leftlines[line] or "The first club following" in leftlines[line] \
                        or "respectively indicate" in leftlines[line] or 'Club abbreviations, not included' in \
                            leftlines[line] or 'Original from' in leftlines[line] or 'CLUB ABBREVIATIONS' in leftlines[line]:
                        is_club_page = True
                is_main_page = False
                if city+str(year) in CLUB_PAGE:
                    if i > CLUB_PAGE[city+str(year)]:
                        is_main_page = True
                else:
                    is_main_page = True
                if is_club_page is False and is_main_page is True:
                    #print(left_txt)
                    if os.path.exists(right_txt):
                        match_family(left_txt, right_txt)
                    elif os.path.exists(left_txt):
                        match_family(left_txt, empty_txt)

        household_dic[city+year] = household
        #print(household_dic)
        data = pd.DataFrame(
            {"city": col_city, "year": col_year, "household_id": col_household, "household_structure": col_hhhead,
             "last_name": col_lastname, "title": col_title, "first_name": col_firstname,
             "middle_names": col_middlename, "suffix": col_suffix,
             "spouse_name": col_spousename, "spouse_middle_names": col_spousemiddle,
             "spouse_last_name": col_spouselast, "spouse_lastsurname": col_spouselastsurname, "new_marriage": col_marriage,
             "clubs_abbr": clubs_raw, "clubs_extended": clubs_clean, "college": college, "grad_year": grad_year,
             "foreign": foreign,
             "died": died, "address": col_address, "new_register": newregister})
        csvfile = csvpath + city + ' ' + year + ".csv"
        if os.path.exists(csvfile):
            os.remove(csvfile)
        data.to_csv(csvfile, index=False)


# In[16]:

def clean_address_single(address: list):
    for key in CORRECT_ADDRESS:
        for WRONG_ADDRESS in CORRECT_ADDRESS[key]:
            if re.search(WRONG_ADDRESS, address) is not None:
                address = re.sub(WRONG_ADDRESS, key, address)

    address = re.sub(TRIVIAL, '', address)
    address = re.sub(TIME, '', address)
    address = re.sub(PHONE, '', address)
    address = re.sub(r"([A-Z])([A-Z])", r"\1 \2", address)
    address = re.sub(r"([A-z]?[a-z]{1,})([A-Z])", r"\1 \2", address)
    address = re.sub(r"([A-Za-z]+)([0-9]+)", r"\1 \2", address)
    address = re.sub(r"([0-9]+)([A-Za-z]+)", r"\1 \2", address)
    address = re.sub('^\s+', '', address)
    address = re.sub(OTHER2, '', address)

    if re.search(ELSE, address) is not None or re.search(OTHER, address) is not None:
        address = ""
    elif address.isspace():
        address = ""

    return address


# Create the result for a single line of  household
def generate_result_single(inputlines: list):
    global household
    global marriage

    if len(inputlines) != 0:
        k = 0
        while k < len(inputlines):
            if marriage == 1:
                break
            if "MARRIAGES OF" in inputlines[k] or "Marriages OF" in inputlines[k] \
                    or "Marriages Of" in inputlines[k] or "Marriages of" in inputlines[k]:
                marriage = 1
                break
            # print(inputlines[k])
            name_and_address = None
            notitle_and_address = None
            spouse_full_name = None
            multiple_and_address = None

            full_name = re.search(EXTREME_TITLE_DETECTION, inputlines[k])
            notitle_name = re.search(NOTITLE_DETECTION, inputlines[k])
            multiple_name = re.search(MULTIPLE_DETECTION, inputlines[k])
            #("full name", re.findall(EXTREME_TITLE_DETECTION, inputlines[k]))
            if k < len(inputlines) - 1:
                spouse_full_name = re.search(EXTREME_TITLE_DETECTION, inputlines[k + 1])

            # if re.search (JUNIOR_DETECTION, inputlines[k]) is not None or re.search (OTHER_DETECTION, inputlines[k]) is not None:
            # continue
            if re.search(MULTIPLE_ADDRESS_DETECTION,inputlines[k]) is not None:
                multiple_and_address = re.search(MULTIPLE_ADDRESS_DETECTION, inputlines[k])
            elif re.search(MULTIPLE_ADDRESS_DETECTION_EXACT,inputlines[k]) is not None:
                multiple_and_address = re.search(MULTIPLE_ADDRESS_DETECTION_EXACT, inputlines[k])
            elif re.search(NAME_ADDRESS_DETECTION, inputlines[k]) is not None:
                name_and_address = re.search(NAME_ADDRESS_DETECTION, inputlines[k])
                #print("address detection", re.findall(NAME_ADDRESS_DETECTION, inputlines[k]))
            elif re.search(NAME_ADDRESS_DETECTION_EXACT, inputlines[k]) is not None:
                name_and_address = re.search(NAME_ADDRESS_DETECTION_EXACT, inputlines[k])
                #print("address detection exact", re.findall(NAME_ADDRESS_DETECTION_EXACT, inputlines[k]))
            elif re.search(NOTITLE_ADDRESS_DETECTION,inputlines[k]) is not None:
                notitle_and_address = re.search(NOTITLE_ADDRESS_DETECTION, inputlines[k])
            elif re.search(NOTITLE_ADDRESS_DETECTION_EXACT,inputlines[k]) is not None:
                notitle_and_address = re.search(NOTITLE_ADDRESS_DETECTION_EXACT, inputlines[k])

            if name_and_address is not None or multiple_and_address is not None or notitle_and_address is not None\
                or full_name is not None or notitle_name is not None or multiple_name is not None:
                # print("C",k,inputlines[k])

                if re.search(MULTIPLE_ADDRESS_DETECTION, inputlines[k]) is not None:
                    addr_origin = clean_address_single(multiple_and_address.group(19) + multiple_and_address.group(20))
                    # print(addr_origin)
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(MULTIPLE_ADDRESS_DETECTION_EXACT, inputlines[k]) is not None:
                    addr_origin = clean_address_single(multiple_and_address.group(17))
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(NAME_ADDRESS_DETECTION, inputlines[k]) is not None:
                    addr_origin = clean_address_single(name_and_address.group(17) + name_and_address.group(18))
                    # print(addr_origin)
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(NAME_ADDRESS_DETECTION_EXACT, inputlines[k]) is not None:
                    addr_origin = clean_address_single(name_and_address.group(15))
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(NOTITLE_ADDRESS_DETECTION, inputlines[k]) is not None:
                    addr_origin = clean_address_single(notitle_and_address.group(14)+notitle_and_address.group(15))
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(NOTITLE_ADDRESS_DETECTION_EXACT, inputlines[k]) is not None:
                    addr_origin = clean_address_single(notitle_and_address.group(12))
                    if re.search(MOVE, addr_origin) is not None:
                        addr = re.sub(MOVE, '', addr_origin)
                        move = re.search(MOVE, addr_origin).group(2)
                        col_address.append(addr)
                        newregister.append(move)
                    else:
                        col_address.append(addr_origin)
                        newregister.append('')
                elif re.search(MULTIPLE_DETECTION, inputlines[k]) is not None:
                    col_address.append('')
                    newregister.append('')
                elif re.search(EXTREME_TITLE_DETECTION, inputlines[k]) is not None:
                    col_address.append('')
                    newregister.append('')
                elif re.search(NOTITLE_DETECTION, inputlines[k]) is not None:
                    col_address.append('')
                    newregister.append('')

                # try:
                #    line_for_information = inputlines[k] + re.search("(\[)(.*)", inputlines[k + 1]).group(2)
                # except:
                #    line_for_information = inputlines[k]

                if re.search('Died ', inputlines[k]) is not None:
                    die = 1
                else:
                    die = 0
                died.append(die)

                try:
                    foreign.append(re.search(FOREIGN_DETECTION, inputlines[k]).group(9))
                except:
                    foreign.append("No")

                household += 1
                col_household.append(household)

                col_city.append(city)
                col_year.append(year)

                if re.search("Married",inputlines[k]) is not None and full_name is not None and spouse_full_name is not None:
                    # print("Case1",full_name, inputlines[k])
                    col_marriage.append("1")
                    col_lastname.append(add_spaces(full_name.group(1), "STRING"))
                    col_title.append(add_spaces(full_name.group(2), "STRING"))
                    first, middle, suffix = get_firstmiddle(full_name.group(4))
                    col_firstname.append(first)
                    col_middlename.append(middle)
                    col_suffix.append(suffix)

                    col_spouselastsurname.append('None')
                    col_spouselast.append(add_spaces(spouse_full_name.group(1), "STRING"))
                    first, middle, suffix = get_firstmiddle(spouse_full_name.group(4))
                    col_spousename.append(first)
                    col_spousemiddle.append(middle)
                    col_hhhead.append('1')

                    clubs_raw.append('')
                    clubs_clean.append('')
                    grad_year.append('')
                    college.append('')

                    inputlines.pop(k + 1)

                elif multiple_and_address is not None or multiple_name is not None:
                    col_lastname.extend([multiple_name.group(1)] * 2)
                    col_title.extend([multiple_name.group(2)] * 2)

                    first_name1, middle_name1, suffix_name1 = get_firstmiddle(multiple_name.group(3))
                    first_name2, middle_name2, suffix_name2 = get_firstmiddle(multiple_name.group(10))
                    col_firstname.append(first_name1)
                    col_middlename.append(middle_name1)
                    col_suffix.append(suffix_name1)
                    col_firstname.append(first_name2)
                    col_middlename.append(middle_name2)
                    col_suffix.append(suffix_name2)

                    if multiple_name.group(8) is not None:
                        raw, clean, grad, colle = get_club(multiple_name.group(8))
                        clubs_raw.append(raw)
                        clubs_clean.append(clean)
                        grad_year.append(grad)
                        college.append(colle)
                    else:
                        clubs_raw.append('')
                        clubs_clean.append('')
                        grad_year.append('')
                        college.append('')
                    if multiple_name.group(15) is not None:
                        raw, clean, grad, colle = get_club(multiple_name.group(15))
                        clubs_raw.append(raw)
                        clubs_clean.append(clean)
                        grad_year.append(grad)
                        college.append(colle)
                    else:
                        clubs_raw.append('')
                        clubs_clean.append('')
                        grad_year.append('')
                        college.append('')

                    col_spousename.extend(['None'] * 2)
                    col_spouselast.extend(['None'] * 2)
                    col_spousemiddle.extend(['None'] * 2)
                    col_spouselastsurname.extend(['None'] * 2)
                    col_household.append(col_household[-1])
                    col_hhhead.extend(['0'] * 2)
                    col_city.append(col_city[-1])
                    col_year.append(col_year[-1])
                    col_address.append(col_address[-1])
                    newregister.append(newregister[-1])
                    foreign.append(foreign[-1])
                    col_marriage.extend(['0'] * 2)
                    died.append('0')

                elif name_and_address is not None or full_name is not None:
                    # print("Case2", name_and_address, inputlines[k])
                    col_marriage.append("0")
                    col_lastname.append(add_spaces(full_name.group(1), "STRING"))
                    col_title.append(add_spaces(full_name.group(2), "STRING"))
                    first, middle, suffix = get_firstmiddle(full_name.group(4))
                    col_firstname.append(first)
                    col_middlename.append(middle)
                    col_suffix.append(suffix)

                    if full_name.group(12) is not None:
                        col_hhhead.append('1')
                        spouse_first, spouse_middle, spouse_last, spouse_lastsurname = get_spousename(
                            full_name.group(12))
                        col_spousename.append(spouse_first)
                        col_spouselast.append(spouse_last)
                        col_spousemiddle.append(spouse_middle)
                        col_spouselastsurname.append(spouse_lastsurname)
                    else:
                        col_hhhead.append('0')
                        col_spousename.append('None')
                        col_spouselast.append('None')
                        col_spousemiddle.append('None')
                        col_spouselastsurname.append('None')

                    if full_name.group(13) is not None:
                        raw, clean, grad, colle = get_club(full_name.group(13))
                        clubs_raw.append(raw)
                        clubs_clean.append(clean)
                        grad_year.append(grad)
                        college.append(colle)
                    else:
                        clubs_raw.append('')
                        clubs_clean.append('')
                        grad_year.append('')
                        college.append('')

                elif notitle_and_address is not None or notitle_name is not None:
                    # print("Case3", notitle_and_address, inputlines[k])
                    col_marriage.append("0")
                    col_title.append('')
                    first, middle, last, suffix = get_notitlename(notitle_name.group(1))
                    col_firstname.append(first)
                    col_middlename.append(middle)
                    col_lastname.append(last)
                    col_suffix.append(suffix)

                    if notitle_name.group(9) is not None:
                        col_hhhead.append('1')
                        spouse_first, spouse_middle, spouse_last, spouse_lastsurname = get_spousename(
                            notitle_name.group(9))
                        col_spousename.append(spouse_first)
                        col_spouselast.append(spouse_last)
                        col_spousemiddle.append(spouse_middle)
                        col_spouselastsurname.append(spouse_lastsurname)
                    else:
                        col_hhhead.append('0')
                        col_spousename.append('None')
                        col_spouselast.append('None')
                        col_spousemiddle.append('None')
                        col_spouselastsurname.append('None')

                    if notitle_name.group(10) is not None:
                        raw, clean, grad, colle = get_club(notitle_name.group(10))
                        clubs_raw.append(raw)
                        clubs_clean.append(clean)
                        grad_year.append(grad)
                        college.append(colle)
                    else:
                        clubs_raw.append('')
                        clubs_clean.append('')
                        grad_year.append('')
                        college.append('')
            k += 1

    if any(len(lst) != len(col_city) for lst in
           [newregister, col_city, col_year, col_lastname, col_title, col_middlename, col_firstname, col_spousename,
            col_spousemiddle, col_spouselast, col_address, col_household, col_hhhead, clubs_raw, clubs_clean, grad_year,
            foreign, died,college, col_marriage, col_suffix, col_spouselastsurname]):
        print("city:", col_city[-2:], "year:", col_year[-2:], "household_id:", col_household[-2:],
              "household_structure:", col_hhhead[-2:],
              "last_name:", col_lastname[-2:], "title:", col_title[-2:], "first_name:", col_firstname[-2:],
              "middle_names:", col_middlename[-2:], "suffix:", col_suffix[-2:],
              "spouse_name:", col_spousename[-2:], "spouse_middle_names:", col_spousemiddle[-2:], "spouse_last_name:",
              col_spouselast[-2:],"spouse_lastsurname:",col_spouselastsurname[-2:],
              "clubs_abbr:", clubs_raw[-2:], "clubs_extended:", clubs_clean[-2:], "grad_year:", grad_year[-2:],"college:", college[-2:],
              "foreign:", foreign[-2:], "died:", died[-2:], "address:", col_address[-2:], "new_register:", "marriage:", col_marriage,
              newregister[-2:])
        print("city:", len(col_city), "year:", len(col_year), "household_id:", len(col_household),
              "household_structure:", len(col_hhhead),
              "last_name:", len(col_lastname), "title:", len(col_title), "first_name:", len(col_firstname),
              "middle_names:", len(col_middlename), "suffix:", len(col_suffix),
              "spouse_name:", len(col_spousename), "spouse_middle_names:", len(col_spousemiddle), "spouse_last_name:",
              len(col_spouselast), "spouse_lastsurname:",len(col_spouselastsurname),
              "clubs_abbr:", len(clubs_raw), "clubs_extended:", len(clubs_clean), "grad_year:", len(grad_year),
              "foreign:", len(foreign), "college:", len(college), "marriage:", len(col_marriage),
              "died:", len(died), "address:", len(col_address), "new_register:", len(newregister))

    return  col_spouselastsurname,col_suffix, col_marriage, newregister, household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address


# In[17]:


def match_single(input_txt: str):
    inputtxt = open(input_txt, 'r', encoding="UTF-8")
    inputlines = inputtxt.readlines()
    # print("A",len(inputlines),inputlines)

    inputlines = clean_blank(inputlines)
    inputlines = general_cleaner(inputlines)
    inputlines = concat_lines(inputlines)
    # print("B", len(inputlines), inputlines)
    col_spouselastsurname, col_suffix,  col_marriage, newregister, household, clubs_raw, clubs_clean, college, grad_year, foreign, died, col_city, col_year, col_household, col_hhhead, col_lastname, col_title, col_middlename, col_firstname, col_spousename, col_spouselast, col_spousemiddle, col_address = generate_result_single(
        inputlines)


# In[19]:


##Set the path for the input txts of single line household
workdir = "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\"
csvpath = workdir + "csv_output\\"
for txtpath, txtdirs, _ in os.walk(workdir + "text_output_single"):
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
        col_marriage = []
        col_spouselastsurname = []
        col_suffix = []
        # household = int(household_dic[city+year])
        household = 100000
        marriage = 0

        for i in range(1, 2000):
            input_txt = os.path.join(txtpath, city + ' ' + year, "pic" + str(i).zfill(3) + ".txt")
            if os.path.exists(input_txt):
                is_club_page = False
                leftlines = open(input_txt, 'r', encoding="UTF-8").readlines()
                for line in range(len(leftlines)):
                    if "The date following" in leftlines[line] or "The first club following" in leftlines[line] \
                            or "respectively indicate" in leftlines[line] or 'Club abbreviations, not included' in \
                            leftlines[line] or 'Original from' in leftlines[line] or 'CLUB ABBREVIATIONS' in leftlines[line]:
                        is_club_page = True
                is_main_page = False
                if city + str(year) in CLUB_PAGE:
                    if i > CLUB_PAGE[city + str(year)]:
                        is_main_page = True
                else:
                    is_main_page = True
                if is_club_page is False and is_main_page is True:
                    match_single(input_txt)

        data = pd.DataFrame(
            {"city": col_city, "year": col_year, "household_id": col_household, "household_structure": col_hhhead,
             "last_name": col_lastname, "title": col_title, "first_name": col_firstname, "middle_names": col_middlename,
             "suffix": col_suffix,
             "spouse_name": col_spousename, "spouse_middle_names": col_spousemiddle, "spouse_last_name": col_spouselast,
             "spouse_lastsurname": col_spouselastsurname,"new_marriage": col_marriage,
             "clubs_abbr": clubs_raw, "clubs_extended": clubs_clean, "college": college, "grad_year": grad_year,
             "foreign": foreign,
             "died": died, "address": col_address, "new_register": newregister})
        csvfile = csvpath + city + ' ' + year + ".csv"
        data.to_csv(csvfile, mode='a+', index=False, header = False)

# In[ ]:




