import pandas as pd
import numpy as np
import os
import re

STATE_LIST = {
    'New Jersey': ['\\bN J[ ]*$', '\\bNJ[ ]*$','Newark N J', 'Summit[ ]*$', 'Morristown[ ]*$', 'Englewood[ ]*$', 'Orange[ ]*$'],
    'New York': ['\\bN Y[ ]*$', '\\bNY[ ]*$', 'Westchester[ ]*$', 'Buffalo[ ]*$', 'Albany[ ]*$', 'New Rochelle','N Rochelle[ ]*$' 'Yonkers[ ]*$', "\\bRye[ ]*$", "\bN York[ ]*$", "\bN work[ ]*$", "\bNark York[ ]*$", "\bNerk Tew[ ]*$", "\bNetwork Tew[ ]*$", "\bNew York[ ]*$", "\bNewark York[ ]*$", "\bNewerk York[ ]*$", "\bNewrk York[ ]*$", "\bNewwork[ ]*$", "\bNirk Tew York[ ]*$", "\bNirk York[ ]*$", "\bNk Tew York[ ]*$", "\bNk York[ ]*$", "\bNo work New[ ]*$", "\bNock[ ]*$", "\bNock York[ ]*$", "\bNok Tew[ ]*$", "\bNok York[ ]*$" ,"\bNoork[ ]*$", "\bNork[ ]*$", "\bNorkew[ ]*$", "\bNorklew[ ]*$", "\bNort[ ]*$",  "\bNowork[ ]*$", "\bNrk[ ]*$", "\bNurklew[ ]*$", "\bNwork[ ]*$","\bNyerk[ ]*$",'\\bBuff[ ]*$',"\\bBualo[ ]*$", "\\bBuf[ ]*$", "\\bBuf\) alo[ ]*$", "\\bBuff[ ]*$", "\\bBuff Quff alo", "\\bBuff lo[ ]*$", "\\bBuffe[ ]*$", "\\bButt[ ]*$", "\\bButtuff[ ]*$", "\\bBuuff[ ]*$",
                 'Brooklyn*$', "B\\'klyn*$", "bkln*$",'Bronx*$','The Bronx*$','Queens*$','Kings*$','Richmond*$'],
    'Georgia': ['\\bGa[ ]*$', '\\bGA[ ]*$'],
    'Pennsylvania': ['\\bPhila[ ]*$', 'Pittsburgh[ ]*$', '\\bPitts[ ]*$', "\\bPargh tts[ ]*$", "\\bPburgh[ ]*$",'\\bPitts[ ]*$','\\bPurgh[ ]*$','\\bburgh[ ]*$','\\bburg[ ]*$','Pitts Iburgh','Purghtts[ ]*$',"\\bPith tts[ ]*$", "\\bPitt[ ]*$", "\\bPittburgh", "\\bPittigh[ ]*$", "\\bPitts h[ ]*$", "\\bPittsburg", "\\bPittsburgh", "\\bPittsurg[ ]*$", "\\bPitturgh[ ]*$","\\bPurg tts[ ]*$", "\\bPurgaitts", "\\bPurgh[ ]*$", "\\bPurghitts", "\\bPurghts[ ]*$", "\\bRigh[ ]*$", "\\bRighburgh", "\\bRitburgh", "\\bRitt[ ]*$", "\\bRittburgh", "\\bRitteburgh", "\\bRittighburgh",'Philadelphia','\\bPa[ ]*$','\\bPaa[ ]*$','\\bPhil[ ]*$',"\\bPhaila[ ]*$", "\\bPhi[ ]*$", "\\bPhi Pa[ ]*$", "\\bPhihila Pa[ ]*$", "\\bPhil Pa[ ]*$", "\\bPhilahila[ ]*$", "\\bPhilail[ ]*$", "\\bPhilaone[ ]*$", "\\bPhila[ ]*$", "\\bPhilbila[ ]*$", "\\bPhile[ ]*$", "\\bPhili[ ]*$", "\\bPhilip[ ]*$", "\\bPhils Pa[ ]*$"],
    'New Hampshire': ['\\bN H[ ]*$', '\\bNH[ ]*$'],
    'Rhode Island': ['\\bR I[ ]*$', '\\bRI[ ]*$', '\\bR 1[ ]*$', '\\bR1[ ]*$', 'Providence', '\\bProv[ ]*$','\\bProvi[ ]*$','\\bdence[ ]*$',"\\bDrovi de nce\\b", "\\bDrovi dence\\b", "\\bDrov[ ]*$", "\\bP dence[ ]*$", "\\bP rovi[ ]*$", "\\bP vis[ ]*$", "\\bP'dence[ ]*$", "\\bPedence[ ]*$", "\\bPence[ ]*$",'Pioniedence', "\\bPordenee", "\\bPorovi[ ]*$", "\\bPorovidence", "\\bPortrovi\\b", "\\bPredence\\b", "\\bPrice Collier", "\\bPro[ ]*$", "\\bProd[ ]*$", "\\bProde[ ]*$", "\\bProdence", "\bPron[ ]*$","\bProndence", "\\bProrovidence", "\\bProv[ ]*$", "\\bProvdo[ ]*$", "\\bProvi[ ]*$", "\\bProvide", 'Newport[ ]*$'],
    'Connecticut': ['\\bConn[ ]*$', 'New Haven', '\\bCt[ ]*$', '\\bC T[ ]*$'],
    'Massachusetts': ['\\bMass[ ]*$', '\\bM A[ ]*$', '\\bMa[ ]*$', '\\bMaa[ ]*$','Boston[ ]*$','B [0-9]{2} ton[ ]*$','B [0-9]{2}[ ]*$','\\bB ton[ ]*$','\\bBon[ ]*$','\\bBoon[ ]*$','\\bBooton[ ]*$','\\bBoton[ ]*$','\\bB on[ ]*$','\\bB Os[ ]*$','\\bB Son[ ]*$','B ton [0-9]{2}',"\\bB ton Os ton\\b", "\\bB tonos[ ]*$", "\\bB tonton[ ]*$", "\\bBo Oton[ ]*$", "\\bBo Ros ton[ ]*$", "\\bBo ton[ ]*$", "\\bBon Dton[ ]*$", "\\bBtonton[ ]*$", "\\bBootonoston\\b", "\\bBosn[ ]*$", "\\bBoton[ ]*$", "\\bBotonton\\b", "\\bBton[ ]*$", "\\bBo Qos[ ]*$", "\\bBo Ros[ ]*$", "\\bBo Ros ton[ ]*$", "\\bBo on[ ]*$", "\\bBo ton[ ]*$", "\\bBoccon[ ]*$", "\\bBocon[ ]*$", "\\bBon[ ]*$", "\\bBon Dos[ ]*$", "\\bBon Dos ton Oton\\b", "\\bBon Dton[ ]*$", "\\bBon Oton[ ]*$", "\\bBon Qos[ ]*$", "\\bBon Ros[ ]*$", "\\bBonos[ ]*$", "\\bBonton[ ]*$", "\\bBoo[ ]*$", "\\bBoo Dos[ ]*$", "\\bBoon>[ ]*$", "\\bBoos[ ]*$", "\\bBooston[ ]*$", "\\bBooton[ ]*$", "\\bBootonoston\\b", "\\bBotonton[ ]*$", "\\bBotop[ ]*$"],
    'Maryland': ['Maryland[ ]*$', '\\bMD[ ]*$', '\\bMd[ ]*$', '\\bM D[ ]*$','Baltimore[ ]*$',"Balalti[ ]*$", "Balo premore[ ]*$", "Balt aore[ ]*$", "Balti[ ]*$", "Balti Dmore[ ]*$", "Balti Omore[ ]*$", "Balti ore[ ]*$", "Baltmore[ ]*$", "Battalti[ ]*$","\\bBraltimore[ ]*$", "\\bBre Qalti more", "\\bBrealti[ ]*$", "\\bBrealtimore"],
    'Alabama': ['\\bA L[ ]*$', '\\bAl[ ]*$', '\\bAla[ ]*$'],
    'California': ['\\bC A[ ]*$', '\\bCa[ ]*$', '\\bCa[ ]*$', '\\bCA[ ]*$', '\\bCal[ ]*$', "\bScaf[ ]*$", "\bScafouthdena[ ]*$", "\bScalif[ ]*$", "\bScalif Couth[ ]*$", "\bScalif F W[ ]*$", "\bScalifouth[ ]*$", "\bScouth[ ]*$", "\bSouth Cali[ ]*$", "\bSouth Cali ![ ]*$", "\bSouth Calif[ ]*$", "\bSouthasa[ ]*$", "\bSouthasadena Calif[ ]*$", "\bSouthe Calif[ ]*$"
                   'Los Angeles','\\bSF\\b', '\\bS F\\b','\\bSan Fran\\b','S EFran', 'San Tran','Sanavanah', 'San Francisco', '\\bSF[ ]*$', '\\bS F[ ]*$', 'Hanford[ ]*$', 'Santa Barbara'],
    'District of Columbia': ['Wash D C[ ]*$', 'Washington D C', 'D CWa[ ]*$', 'D C[ ]*$','DC W[ ]*$','W DC[ ]*$','Wh D C[ ]*$','Wh Tash[ ]*$','Wa{1,3}sh[ D C]?[ ]*$','Washington[ ]*$','Wa ash D C[ ]*$','Wash W BD C[ ]*$','\\bWh[ ]*$',"\\bWesh[ ]*$","\\bWh Jash D C[ ]*$", "\\bWhash[ ]*$", "\\bWhash D C[ ]*$", "\\bWi[ ]*", "\\bWi Jash[ ]*$", "\\bWi ash D C[ ]*$", "\\bWiash[ ]*$", "\\bWin C Bruce", "\\bWis[ ]*$", "\\bWish[ ]*$", "\\bWishash[ ]*$"],
    'Delaware': ['Delaware[ ]*$', '\\bDel[ ]*$', 'Wilmington[ ]*$'],
    'Iowa': ['\\bIA[ ]*$', '\\bI A[ ]*$', '\\bIa[ ]*$'],
    'Louisiana': ['Louisiana[ ]*$', '\\bLA[ ]*$', '\\bL A[ ]*$', '\\bLa[ ]*$', 'New Orleans',"\\bNew leans[ ]*$", "\\bNow rleans[ ]*$"],
    'Indiana': ['Indiana[ ]*$', '\\bIN[ ]*$', '\\bI N[ ]*$'],
    'Illinois': ['Illinois[ ]*$', '\\bIl[ ]*$', '\\bI L[ ]*$', 'Chicago[ ]*$','Ch Thio Jago','Chioago[ ]*$','\\bChoio[ ]*$','Chro Jago[ ]*$','Ch鹿hio[ ]*$','Co Chio[ ]*$','Cohicago[ ]*$','Chic ago[ ]*$','\\bChi[aosec][ ]*$','Ch.*Jago','Chago[ ]*$',"\\bChe Cago[ ]*$", "\\bChe Chic[ ]*$", "\\bChe Jago[ ]*$", "\\bCheago[ ]*$", "\\bChehic Jago[ ]*$", "\\bChhic[ ]*$", "\\bChhic Jago[ ]*$", "\\bChhic Vago[ ]*$", "\\bChhicago[ ]*$", "\\bChhie[ ]*$", "\\bChhieago[ ]*$", "\\bChhio[ ]*$", "\\bChhioago[ ]*$", "\\bChi[ ]*$", "\\bChi Jago[ ]*$", "\\bChi The[ ]*$", "\\bChi Vago[ ]*$", "\\bChia[ ]*$", "\\bChiage[ ]*$", "\\bChiago[ ]*$", "\\bChic Jago[ ]*$", "\\bChic Vago[ ]*$", "\\bChie[ ]*$", "\\bChie Cago[ ]*$", "\\bChie Jago[ ]*$", "\\bChieago[ ]*$", "\\bChielago[ ]*$", "\\bChijago[ ]*$", "\\bChio[ ]*$", "\\bChio Jago[ ]*$", "\\bChio Vago[ ]*$", "\\bCho[ ]*$", "\\bChioago[ ]*$", "\\bChis Jago[ ]*$", "\\bChic ago[ ]*$", "\\bChie Jago[ ]*$", "\\bCho Jago[ ]*$", "\\bChohic[ ]*$", "\\bChoio[ ]*$", "\\bChro[ ]*$", "\\bChro Jago[ ]*$", "\\bChroago[ ]*$", "\\bChrohic[ ]*$", "\\bChrohicago[ ]*$", "\\bCo Chic ago[ ]*$", "\\bCo Chio[ ]*$", "\\bCo Jago[ ]*$", "\\bCo Thio Jago[ ]*$", "\\bCoago[ ]*$", "\\bCohic[ ]*$", "\\bCohic Jago[ ]*$", "\\bCohicago[ ]*$", "\\bCro Jago[ ]*$"],
    'Kansas': ['Kansas[ ]*$', '\\bKan[ ]*$', '\\bKS[ ]*$', '\\bK S[ ]*$'],
    'Michigan': ['Michigan', '\\bMi[ ]*$', '\\bMI[ ]*$', '\\bM I[ ]*$', 'Detroit[ ]*$', '\\bMich[ ]*$'],
    'Minnesota': ['\\bMinn[ ]*$', 'Minnesota', '\\bMN[ ]*$', '\\bM N[ ]*$', 'Minneapolis','St Paul[ ]*$'],
    'Missouri': ['Missouri', '\\bMiss[ ]*$', '\\bMO[ ]*$', '\\bM O[ ]*$', 'St Louis','Siouis[ ]*$'],
    'Montana': ['Montana[ ]*$'],
    'Ohio': ['Ohio[ ]*$', '\\bOh[ ]*$', '\\bOH[ ]*$', '\\bO H[ ]*$', 'Cleveland','Powell[ ]*$','Newark O[ ]*$'],
    'Washington': ['Seattle[ ]*$'],
    'Vermont': ['\\bVt[ ]*$', '\\bVT[ ]*$', '\\bV T[ ]*$'],
    'Virginia': ['\\bVa[ ]*$', '\\bVA[ ]*$', '\\bV A[ ]*$'],
    'Florida': ['\\bFla[ ]*$', 'Fernandina'],
    'South Carolina': ['\\bS C[ ]*$', '\\bSC[ ]*$','S Carolina',"\\bSarolina\\b"],
    'North Carolina': ['\\bN C[ ]*$', '\\bNC[ ]*$','N Carolina',"\\bNarolina\\b"],
}

CITY_LIST = {
    'Philadelphia': ['Phila[ ]*$', 'Philadelphia[ ]*$','\\bPa[ ]*$','\\bPaa[ ]*$','\\bPhil[ ]*$',"\\bPhaila[ ]*$", "\\bPhi[ ]*$", "\\bPhi Pa[ ]*$", "\\bPhihila Pa[ ]*$", "\\bPhil Pa[ ]*$", "\\bPhilahila[ ]*$", "\\bPhilail[ ]*$", "\\bPhilaone[ ]*$", "\\bPhila[ ]*$", "\\bPhilbila[ ]*$", "\\bPhile[ ]*$", "\\bPhili[ ]*$", "\\bPhilip[ ]*$", "\\bPhils Pa[ ]*$"],
    'Washington': ['Wash D C[ ]*$', 'Washington D C', 'D CWa[ ]*$', 'D C[ ]*$','DC W[ ]*$','W DC[ ]*$','Wh D C[ ]*$','Wh Tash[ ]*$','Wa{1,3}sh[ D C]?[ ]*$','Washington[ ]*$','Wa ash D C[ ]*$','Wash W BD C[ ]*$','\\bWh[ ]*$',"\\bWesh[ ]*$","\\bWh Jash D C[ ]*$", "\\bWhash[ ]*$", "\\bWhash D C[ ]*$", "\\bWi[ ]*$", "\\bWi Jash[ ]*$", "\\bWi ash D C[ ]*$", "\\bWiash[ ]*$", "\\bWin C Bruce", "\\bWis[ ]*$", "\\bWish[ ]*$", "\\bWishash[ ]*$"],
    'Boston': ['Boston[ ]*$','B [0-9]{2} ton[ ]*$','B [0-9]{2}[ ]*$','\\bB ton[ ]*$','\\bBon[ ]*$','\\bBoon[ ]*$','\\bBooton[ ]*$','\\bBoton[ ]*$','\\bB on[ ]*$','\\bB Os[ ]*$','\\bB Son[ ]*$','B ton [0-9]{2}',"\\bB ton Os ton\\b", "\\bB tonos[ ]*$", "\\bB tonton[ ]*$", "\\bBo Oton[ ]*$", "\\bBo Ros ton[ ]*$", "\\bBo ton[ ]*$", "\\bBon Dton[ ]*$", "\\bBtonton[ ]*$", "\\bBootonoston\\b", "\\bBosn[ ]*$", "\\bBoton[ ]*$", "\\bBotonton\\b", "\\bBton[ ]*$", "\\bBo Qos[ ]*$", "\\bBo Ros[ ]*$", "\\bBo Ros ton[ ]*$", "\\bBo on[ ]*$", "\\bBo ton[ ]*$", "\\bBoccon[ ]*$", "\\bBocon[ ]*$", "\\bBon[ ]*$", "\\bBon Dos[ ]*$", "\\bBon Dos ton Oton\\b", "\\bBon Dton[ ]*$", "\\bBon Oton[ ]*$", "\\bBon Qos[ ]*$", "\\bBon Ros[ ]*$", "\\bBonos[ ]*$", "\\bBonton[ ]*$", "\\bBoo[ ]*$", "\\bBoo Dos[ ]*$", "\\bBoon>[ ]*$", "\\bBoos[ ]*$", "\\bBooston[ ]*$", "\\bBooton[ ]*$", "\\bBootonoston\\b", "\\bBotonton[ ]*$", "\\bBotop[ ]*$"],
    'New Rochell': ['New Rochell[ ]*$'],
    'New York': ['New York','\\bS I[ ]*$', '\\bSI[ ]*$', '\\bS 1[ ]*$', '\\bS1[ ]*$', '\\bL I[ ]*$', '\\bLI[ ]*$', '\\bI I[ ]*$',"\\bN York[ ]*$", "\\bN work[ ]*$", "\\bNark York[ ]*$", "\\bNerk Tew[ ]*$", "\\bNetwork Tew[ ]*$", "\\bNew York[ ]*$", "\\bNewark York[ ]*$", "\\bNewerk York[ ]*$", "\\bNewrk York[ ]*$", "\\bNewwork[ ]*$", "\\bNirk Tew York[ ]*$", "\\bNirk York[ ]*$", "\\bNk Tew York[ ]*$", "\\bNk York[ ]*$", "\\bNo work New[ ]*$", "\\bNock[ ]*$", "\\bNock York[ ]*$", "\\bNok Tew[ ]*$", "\\bNok York[ ]*$" ,"\bNoork[ ]*$", "\bNork[ ]*$", "\\bNorkew[ ]*$", "\\bNorklew[ ]*$", "\\bNort[ ]*$",  "\\bNowork[ ]*$", "\\bNrk[ ]*$", "\\bNurklew[ ]*$", "\\bNwork[ ]*$",'\\bNyerk[ ]*$'],
    'Summit': ['Summit[ ]*$'],
    'Newark': ['Newark[ ]*$'],
    'Baltimore': ['Baltimore[ ]*$',"Balalti[ ]*$", "Balo premore[ ]*$", "Balt aore[ ]*$", "Balti[ ]*$", "Balti Dmore[ ]*$", "Balti Omore[ ]*$", "Balti ore[ ]*$", "Baltmore[ ]*$", "Battalti[ ]*$","\\bBraltimore[ ]*$", "\\bBre Qalti more", "\\bBrealti[ ]*$", "\\bBrealtimore"],
    'Buffalo': ['Buffalo[ ]*$','\\bBuff[ ]*$',"\\bBualo[ ]*$", "\\bBuf[ ]*$", "\\bBuf\) alo[ ]*$", "\\bBuff[ ]*$", "\\bBuff Quff alo", "\\bBuff lo[ ]*$", "\\bBuffe[ ]*$", "\\bButt[ ]*$", "\\bButtuff[ ]*$", "\\bBuuff[ ]*$"],
    'Chicago': ['Chicago[ ]*$','Ch Thio Jago','Chioago[ ]*$','\\bChoio[ ]*$','Chro Jago[ ]*$','Ch鹿hio[ ]*$','Co Chio[ ]*$','Cohicago[ ]*$','Chic ago[ ]*$','\\bChi[aosec][ ]*$','Ch.*Jago','Chago[ ]*$',"\\bChe Cago[ ]*$", "\\bChe Chic[ ]*$", "\\bChe Jago[ ]*$", "\\bCheago[ ]*$", "\\bChehic Jago[ ]*$", "\\bChhic[ ]*$", "\\bChhic Jago[ ]*$", "\\bChhic Vago[ ]*$", "\\bChhicago[ ]*$", "\\bChhie[ ]*$", "\\bChhieago[ ]*$", "\\bChhio[ ]*$", "\\bChhioago[ ]*$", "\\bChi[ ]*$", "\\bChi Jago[ ]*$", "\\bChi The[ ]*$", "\\bChi Vago[ ]*$", "\\bChia[ ]*$", "\\bChiage[ ]*$", "\\bChiago[ ]*$", "\\bChic Jago[ ]*$", "\\bChic Vago[ ]*$", "\\bChie[ ]*$", "\\bChie Cago[ ]*$", "\\bChie Jago[ ]*$", "\\bChieago[ ]*$", "\\bChielago[ ]*$", "\\bChijago[ ]*$", "\\bChio[ ]*$", "\\bChio Jago[ ]*$", "\\bChio Vago[ ]*$", "\\bCho[ ]*$", "\\bChioago[ ]*$", "\\bChis Jago[ ]*$", "\\bChic ago[ ]*$", "\\bChie Jago[ ]*$", "\\bCho Jago[ ]*$", "\\bChohic[ ]*$", "\\bChoio[ ]*$", "\\bChro[ ]*$", "\\bChro Jago[ ]*$", "\\bChroago[ ]*$", "\\bChrohic[ ]*$", "\\bChrohicago[ ]*$", "\\bCo Chic ago[ ]*$", "\\bCo Chio[ ]*$", "\\bCo Jago[ ]*$", "\\bCo Thio Jago[ ]*$", "\\bCoago[ ]*$", "\\bCohic[ ]*$", "\\bCohic Jago[ ]*$", "\\bCohicago[ ]*$", "\\bCro Jago[ ]*$"],
    'Cleveland': ['Cleveland[ ]*$','Cloveland[ ]*$'],
    'Detroit': ['Detroit[ ]*$'],
    'Los Angeles': ['Los Angeles[ ]*$'],
    'Minneapolis': ['Minneapolis[ ]*$'],
    'New Orleans': ['New Orleans[ ]*$',"\\bNew leans[ ]*$", "\\bNow rleans[ ]*$"],
    'Pittsburgh': ['Pittsburgh[ ]*$', "\\bPargh tts[ ]*$", "\\bPburgh[ ]*$",'\\bPitts[ ]*$','\\bPurgh[ ]*$','\\bburgh[ ]*$','\\bburg[ ]*$','Pitts Iburgh','Purghtts[ ]*$',"\\bPith tts[ ]*$", "\\bPitt[ ]*$", "\\bPittburgh", "\\bPittigh[ ]*$", "\\bPitts h[ ]*$", "\\bPittsburg", "\\bPittsburgh", "\\bPittsurg[ ]*$", "\\bPitturgh[ ]*$","\\bPurg tts[ ]*$", "\\bPurgaitts", "\\bPurgh[ ]*$", "\\bPurghitts", "\\bPurghts[ ]*$", "\\bRigh[ ]*$", "\\bRighburgh", "\\bRitburgh", "\\bRitt[ ]*$", "\\bRittburgh", "\\bRitteburgh", "\\bRittighburgh"],
    'Providence': ['Providence[ ]*$', '\\bProv[ ]*$','\\bProvi[ ]*$','\\bdence[ ]*$',"\\bDrovi de nce\\b", "\\bDrovi dence\\b", "\\bDrov[ ]*$", "\\bP dence[ ]*$", "\\bP rovi[ ]*$", "\\bP vis[ ]*$", "\\bP'dence[ ]*$", "\\bPedence[ ]*$", "\\bPence[ ]*$",'Pioniedence', "\\bPordenee", "\\bPorovi[ ]*$", "\\bPorovidence", "\\bPortrovi\\b", "\\bPredence\\b", "\\bPrice Collier", "\\bPro[ ]*$", "\\bProd[ ]*$", "\\bProde[ ]*$", "\\bProdence", "\\bPron[ ]*$","\\bProndence", "\\bProrovidence", "\\bProv[ ]*$", "\\bProvdo[ ]*$", "\\bProvi[ ]*$", "\\bProvide"],
    'San Francisco': ['San Francisco', '\\bSF\\b', '\\bS F\\b','\\bSan Fran\\b','S EFran', 'San Tran','Sanavanah'],
    'Seattle': ['Seattle[ ]*$'],
    'St Paul': ['St Paul[ ]*$','\\bPaul[ ]*$'],
    'St Louis': ['St Louis[ ]*$','Siouis[ ]*$'],
    'Hanford': ['Hanford[ ]*$'],
    'Morristown': ['Morristown[ ]*$'],
    'Newport': ['Newport[ ]*$'],
    'Englewood': ['Englewood[ ]*$'],
    'New Haven': ['New Haven[ ]*$'],
    'Wilmington': ['Wilmington[ ]*$'],
    'Orange': ['Orange[ ]*$'],
    'Geneva': ['Geneva[ ]*$'],
    'New Rochelle': ['N Rochelle[ ]*$','New Rochelle'],
    'Yonkers': ['Yonkers[ ]*$'],
    'Rye': ['\\bRye[ ]*$'],
    'Manchester': ['Manchester[ ]*$'],
    'Santa Barbara': ['Santa Barbara[ ]*$'],
    'Powell': ['Powell[ ]*$'],
}

REGISTER_LIST = {
    'Philadelphia': ['Phila', 'Philadelphia','Phil',"Phaila", "Phi", "Phi Pa", "Phihila Pa", "Phil Pa", "Philahila", "Philail", "Philaone", "Phila", "Philbila", "Phile", "Phili", "Philip", "Phils Pa"],
    'Washington': ['Wash D C', 'Wash','Washington D C', 'D CWa', 'D C','DC W','Wh D C','Wh Tash','Wa{1,3}sh[ D C]?','Washington','Wa ash D C','Wash W BD C','Wh[ ]*$',"Wesh","Wh Jash D C", "Whash[ ]*$", "Whash D C", "Wi[ ]*", "Wi Jash", "Wi ash D C", "Wiash", "Win C Bruce", "Wis[ ]*$", "Wish[ ]*$", "Wishash"],
    'Boston': ['Boston','B [0-9]{2} ton','B [0-9]{2}','\\bB ton\\b','\\bBon[ ]*$','\\bBoon[ ]*$','\\bBooton\\b','\\bBoton\\b','B on[ ]*$','\B Os[ ]*$','B Son[ ]*$','B ton [0-9]{2}',"B ton Os ton", "B tonos", "B tonton", "Bo Oton", "Bo Ros ton", "Bo ton", "Bon Dton", "Btonton", "Bootonoston", "Bosn[ ]*$", "Boton[ ]*$", "Botonton", "Bton[ ]*$", "Bo Qos[ ]*$", "Bo Ros[ ]*$", "Bo Ros ton[ ]*$", "Bo on[ ]*$", "Bo ton[ ]*$", "Boccon[ ]*$", "Bocon[ ]*$", "Bon[ ]*$", "Bon Dos[ ]*$", "Bon Dos ton Oton", "Bon Dton[ ]*$", "Bon Oton[ ]*$", "Bon Qos[ ]*$", "Bon Ros[ ]*$", "Bonos", "Bonton", "Boo[ ]*$", "Boo Dos", "Boon>[ ]*$", "Boos[ ]*$", "Booston", "Booton", "Bootonoston", "Botonton", "Botop[ ]*$"],
    'New Rochell': ['New Rochell'],
    'New York': ['New York','\\bS I[ ]*$', '\\bSI[ ]*$', '\\bS 1[ ]*$', '\\bS1[ ]*$', '\\bL I[ ]*$', '\\bLI[ ]*$', '\\bI I[ ]*$',"N York", "N work", "Nark York", "Nerk Tew", "Network Tew", "New", "New York", "Newark", "Newark York", "Newerk York", "Nework", "Newrk", "Newrk York", "Newwork","Nik", "Nirk Tew York", "Nirk York", "Nk Tew York", "Nk York", "No work New", "Nock", "Nock York", "Nok", "Nok Tew", "Nok York", "Nok York Tew York", "Noork", "Nork", "Norkew", "Norklew", "Nort",  "Nowork", "Nrk", "Nurklew", "Nwork",'Nyerk'],
    'Summit': ['Summit'],
    'Albany': ['Albany'],
    'Newark': ['Newark'],
    'Baltimore': ['Baltimore',"Balalti", "Balo premore", "Balt aore", "Balti", "Balti Dmore", "Balti Omore", "Balti ore", "Baltimore", "Baltmore", "Battalti""Braltimore", "Bre Qalti more", "Brealti", "Brealtimore"],
    'Buffalo': ['Buffalo','\\bBuff\\b',"Bualo", "Bub", "Buf\\) alo", "Buff", "Buff Quff alo", "Buff lo", "Buffe", "Butt", "Buttuff", "Buuff"],
    'Chicago': ['Chicago','Ch Thio Jago','Chioago','\\bChoio\\b','Chro Jago','Ch鹿hio','Co Chio','Cohicago','Chic ago','\\bChi[aosec]\\b','Ch.*Jago','Chago',"Che Cago", "Che Chic", "Che Jago", "Cheago", "Chehic Jago", "Chhic", "Chhic Jago", "Chhic Vago", "Chhicago", "Chhie", "Chhieago", "Chhio", "Chhioago", "Chi", "Chi Jago", "Chi Jago", "Chi The", "Chi Vago", "Chia", "Chiage", "Chiago", "Chic Jago", "Chic Vago", "Chie", "Chie Cago", "Chie Jago", "Chieago", "Chielago", "Chijago", "Chio", "Chio Jago", "Chio Vago", "Cho", "Chioag", "Chis Jago", "Chic ago", "Chie Jago", "Cho Jago", "Chohic", "Choio", "Chro", "Chro Jago", "Chroago", "Chrohic", "Chrohicago", "Co Chic ago", "Co Chio", "Co Jago", "Co Thio Jago", "Coago", "Cohic", "Cohic Jago", "Cohicago", "Cro Jago"],
    'Cleveland': ['Cleveland','Cloveland'],
    'Detroit': ['Detroit'],
    'Los Angeles': ['Los Angeles'],
    'Minneapolis': ['Minneapolis'],
    'New Orleans': ['New Orleans',"New leans", "Now rleans"],
    'Pittsburgh': ['Pittsburgh', "Pargh tts", "Pburgh",'\\bPitts\\b','\\bPurgh\\b','\\bburgh\\b','\\bburg\\b','Pitts Iburgh','Purghtts',"Pith tts", "Pitt", "Pittburgh", "Pittigh", "Pitts h", "Pittsburg", "Pittsburgh", "Pittsurg", "Pitturgh","Purg tts", "Purgaitts", "Purgh", "Purghitts", "Purghts", "Righ", "Righburgh", "Ritburgh", "Ritt", "Rittburgh", "Ritteburgh", "Rittighburgh"],
    'Providence': ['Providence', '\\bProv[ ]*$', 'Provi', 'dence', "Drovi de nce", "Drovi dence", "Drov[ ]*$", "P dence", "P rovi[ ]*$", "P vis[ ]*$", "P'dence", "Pedence", "Pence", "Drovi",'Pioniedence',"Pordenee", "Porovi", "Porovidence", "Portrovi", "Predence", "Pro[ ]*$", "Prod[ ]*$", "Prode[ ]*$", "Prodence", "Pron[ ]*$","Prondence", "Prorovidence", "Prov[ ]*$", "Provdo", "Provi[ ]*$", "Provide"],
    'San Francisco': ['San Francisco', '\\bSF\\b', '\\bS F\\b','San Fran','S EFran', 'San Tran','Sanavanah'],
    'Seattle': ['Seattle'],
    'St Louis': ['St Louis',' Siouis'],
    'Hanford': ['Hanford'],
    'Morristown': ['Morristown'],
    'Newport': ['Newport'],
    'Englewood': ['Englewood'],
    'New Haven': ['New Haven'],
    'Wilmington': ['Wilmington'],
    'Orange': ['Orange'],
    'Geneva': ['Geneva'],
    'New Rochelle': ['N Rochelle'],
    'Yonkers': ['Yonkers'],
    'Rye': ['\\bRye[ ]*$'],
    'Manchester': ['Manchester*$'],
    'Santa Barbara': ['Santa Barbara*$'],
    'Powell': ['Powell*$']
}

COUNTY_LIST = {
    'Westchester': ['Westchester', 'Croton on Hudson', 'New Rochell', 'Westches ter', 'Yonkers', '\\bRye[ ]*$'],
    'Morris': ['Morristown[ ]*$'],
    'New Heaven': ['New Heaven[ ]*$'],
    'Bergen': ['Englewood[ ]*$'],
    'Essex': ['Orange[ ]*$'],
    'Ontario and Seneca': ['Geneva[ ]*$'],
    'Hartford': ["Hartford[ ]*$", 'Manchester[ ]*$'],
    'Kings': ['Hanford[ ]*$','Brooklyn', "B\\'klyn", "bkln"],
    'Delaware': ["Delaware[ ]*$",'Powell[ ]*$'],
    'Albany': ['Albany[ ]*$'],
    'Bronx' : ['Bronx*$','The Bronx*$'],
    'Queens' : ['Queens*$'],
    'Richmond' : ['Richmond*$']
}

REGION_LIST = {
    'Staten Island': ['\\bS I[ ]*$', '\\bSI[ ]*$', '\\bS 1[ ]*$', '\\bS1[ ]*$'],
    'Long Island': ['\\bL1[ ]*$', '\\bL I[ ]*$', '\\bLI[ ]*$', '\\bI I[ ]*$'],
    'Brooklyn': ['Brooklyn*$', "B\\'klyn", "bkln"],
    'Pasadena': ['Pasadena*$'],
    'Bronx' : ['Bronx*$','The Bronx*$'],
    'Kings': ['Kings*$']
}

ABBREVIATION_LIST = {
    'Park': ["P\\'k", "\\bPk\\b"],
    'Washington': ["Wash \\'n", "\\bWash\\b"],
    'Avenue': ["\\bAv\\b"],
    'Island': ["Is\\'d"],
    'Morristown': ["Morrist \\'n"],
    'Square': [" Sq[ ]*$"],
    'Brooklyn': ["B\\'klyn", "Bklyn"],
    'Broadway': ["B\\'way"],
    'Madison': ["\\bMad\\b", "Mad ,"],
    'Heights': ['\\bHgts\\b'],
    'Lexington': ['\\bLex\\b', " Lex \\'g\\'n "],
    'Place': ['\\bPl\\b', '\\bP I\\b'],
    'Creek': ["Cr\\'k"],
    'Brighton': ["Bg\\' ton"],
    'Drive': ["\\bDv\\b"],
    'Boulevard': ['Blvd'],
    'Road' :['\\bRd\\b'],
    '': ["螡违", "鈥?", "釓幁 釒?\\* \\*", "釒?", "鹿", "鈥︹€?", "袗谐", "乇賵", "釓?釒?", "鈥漌", "鈧?", "螒谓", "茅", "鈼?", "鈥漃", "鈾?员諉员",
         "貙貙 屑芯写 芯写 ,,", "\\)", "R 袝", "脩","屑邪"]
}

CASUAL = "Dilatoryomiciles|D omicilesilatory|Dflatoryomiciles|Dilatory omiciles|Dilatoryomiciles|D omicilesilatory|Dilatoryomiciles|Dililatoryomiciles|ilatory D omiciles|ilatoryomiciles D|llatory|ilatoryomiciles Da|llatory M  K Dlate|ilatoryomiciles D OR|ilatoryornicile a Da|ilatoryomicilesashsee W|omiciles|ilatoryomiciles Domic|ilatoryomiciles Da|ilatoryomiciles|ilatoryomicile Da|\
         ilatoryomi eiles|ilatoryomi cifer|ilatoryicilesomicil P|ilatory Domiciles|ilatory Da omiciles|ilatory|omicilesilatory|omiciles|D omicileilatory|D omiciles| D omicilesilatory|D!|Da|Da ilatoryomicile s|Da ilatoryomiciles|Dailatoryomiciles|Daomicile s|Datoryomiciles|Datory釒爋miciles|Dh|Di|Di Domiciles ilatory|Diary,ilat贸ry|Dihomiciles|Diilatoryomicilea|Diilatoryomiciles|Diilatoryomicilessee|\
         Dilailatoryomicile|Dilatory|Dilatory omicile a|Dilatory omicile s|Dilatory omiciles|Dilatoryamiciles|Dilatoryciles|Dilatoryomicile|Dilatoryomicile a|Dilatoryomiciles|Dimilatoryomiciles|Diomiciles|Dion|Domicil|Domiciles See Builatory|Domiciles Builatory|D Horniciles| D Ilatory omilciles"

# Your directory path
directory_path = 'C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\csv_output'

for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(directory_path, filename)

        # Read the CSV file
        df = pd.read_csv(file_path)
        vars1 = ['last_name', 'first_name', 'middle_names', 'spouse_name', 'spouse_middle_names','spouse_last_name']
        vars2 = ['address', 'new_register']

        try:
            for var in vars1:
                df[var] = df[var].astype(str)
                df[var] = df[var].replace('nan$', '', regex=True)
                df[var] = df[var].replace(r"\s+", "", regex=True)
                df[var] = df[var].replace(r"([A-Z])([A-Z])", r"\1 \2", regex=True)
                df[var] = df[var].replace(r"([a-z])([A-Z])", r"\1 \2", regex=True)
                df[var] = df[var].replace(r"(-)([A-Za-z])", r"\1 \2", regex=True)
                df[var] = df[var].replace(r"-", "", regex=True)
                df[var] = df[var].apply(lambda x: re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a ])", '', x))
                df[var] = df[var].str.strip()

            for var in vars2:
                df[var] = df[var].astype(str)
                df[var] = df[var].replace('nan$', '', regex=True)
                df[var] = df[var].replace(r"\s+", "", regex=True)
                df[var] = df[var].replace(r"([A-Z])([A-Z])", r"\1 \2", regex=True)
                df[var] = df[var].replace(r"([a-z])([A-Z])", r"\1 \2", regex=True)
                df[var] = df[var].replace(r"([A-Za-z]+)([0-9])", r"\1 \2", regex=True)
                df[var] = df[var].replace(r"([0-9])([A-Za-z]+)", r"\1 \2", regex=True)
                df[var] = df[var].replace(r"-", "", regex=True)
                df[var] = df[var].apply(lambda x: re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a ])", '', x))
                df[var] = df[var].str.strip()

            df['city/town_correct'] = ''
            df['county_correct'] = ''
            df['state_correct'] = ''
            df['region_correct'] = ''
            df['other_city'] = ''
            df['address_original'] = df['address']

            # Check 'address' column against dictionaries
            for index, row in df.iterrows():
                address = row['address']
                register = row['new_register']
                #print(address)

                #if re.search(CASUAL,register) is not None:
                #    df.at[index,'dilatory domiciles'] = '1'
                #else:
               #     df.at[index, 'dilatory domiciles'] = '0'

                for correct, variations in REGISTER_LIST.items():
                    for variant in variations:
                        if re.search(variant, register) is not None:
                            #print(re.search(variant, register))
                            df.at[index, 'other_city'] = correct

                for fullname, abbreviations in ABBREVIATION_LIST.items():
                    for abbr in abbreviations:
                        address = df.at[index, 'address']
                        if re.search(abbr, address) is not None:
                            #print(re.search(abbr, address))
                            df.at[index, 'address'] = re.sub(abbr, fullname, address)

                for correct, variations in CITY_LIST.items():
                    for variant in variations:
                        if re.search(variant, address) is not None:
                            #print(re.search(variant, address))
                            df.at[index, 'city/town_correct'] = correct

                for correct, variations in COUNTY_LIST.items():
                    for variant in variations:
                        if re.search(variant, address) is not None:
                            #print(re.search(variant, address))
                            df.at[index, 'county_correct'] = correct

                for correct, variations in STATE_LIST.items():
                    for variant in variations:
                        if re.search(variant, address) is not None:
                            #print(re.search(variant, address))
                            df.at[index, 'state_correct'] = correct

                for correct, variations in REGION_LIST.items():
                    for variant in variations:
                        if re.search(variant, address) is not None:
                            #print(re.search(variant, address))
                            df.at[index, 'region_correct'] = correct

            df = df.drop('new_register', axis=1)

        except:
            pass
        # Save the DataFrame back to the CSV
        df.to_csv(file_path, index=False)

