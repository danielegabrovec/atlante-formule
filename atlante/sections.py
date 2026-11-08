"""Tassonomia e colori condivisi da navigazione, schede e percorsi."""
from functools import lru_cache
SECTIONS={
 'base':('Matematica','#2463a6','#7bb5f1'),
 'classica':('Matematica','#107a68','#67d1b5'),
 'analitica':('Matematica','#087c91','#69cfe5'),
 'trigonometria':('Matematica','#557325','#b4d16d'),
 'analisi':('Matematica','#4f50a4','#aaa6fa'),
 'multivariabile':('Matematica','#6650a4','#c2a6f3'),
 'lineare':('Matematica','#815099','#d5a4ed'),
 'probabilita':('Matematica','#946012','#edc26c'),
 'meccanica':('Fisica','#a15b20','#f0b67d'),
 'termo':('Fisica','#a24833','#f7ab96'),
 'onde':('Fisica','#167c85','#78d0d5'),
 'elettro':('Fisica','#8b6a0e','#e7cb73'),
 'moderna':('Fisica','#84518d','#d7abe1'),
 'bool':('Elettronica e sistemi','#9c3f71','#efa4cc'),
 'digitale':('Elettronica e sistemi','#3565aa','#93baf8'),
 'discreta':('Matematica','#5256a5','#afb1f9'),
 'numerico':('Matematica','#316992','#91c5ec'),
 'elettronica':('Elettronica e sistemi','#9b620e','#eac574'),
 'segnali':('Elettronica e sistemi','#0e7888','#77d5e3'),
 'robotica':('Elettronica e sistemi','#147c62','#76d9b7'),
 'reti':('Informatica','#23784a','#8ad8aa'),
 'informatica':('Informatica','#4b647b','#b0c6dd'),
 'algoritmi':('Informatica','#3f6a94','#91bee7'),
 'architettura':('Informatica','#576b87','#b4c6e7'),
 'basi_dati':('Informatica','#307b79','#86d7d1'),
 'sicurezza':('Informatica','#985c3c','#eab095'),
 'programmazione':('Informatica','#407256','#9cd6af'),
 'sistemi_operativi':('Informatica','#596c94','#a8bce6'),
 'web':('Informatica','#397d8a','#90d4df'),
 'distribuita':('Intelligenza artificiale','#6e619a','#c4b3ed'),
 'statistica':('Matematica','#886315','#e7c57a'),
 'ottimizzazione':('Matematica','#79519e','#c5a7e9'),
 'ml':('Intelligenza artificiale','#7650b4','#c6a7ff'),
 'deep':('Intelligenza artificiale','#a14888','#efa3d9'),
 'quantum':('Fisica','#5357ae','#b1b4ff'),
 'bioai':('Intelligenza artificiale','#9c5141','#f1b3a5'),
 'visione':('Intelligenza artificiale','#296fa1','#90c8ef'),
 'personali':('Personale','#566b7c','#b3c7d6'),
}

def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722)))

@lru_cache(maxsize=80)
def section_color(key,dark=False):
    entry=SECTIONS.get(key,SECTIONS['personali'])
    color=entry[2 if dark else 1];background='#192d3b' if dark else '#eff7f7'
    for _ in range(30):
        lo,hi=sorted((luminance(color),luminance(background)))
        if (hi+.05)/(lo+.05)>=4.6:return color
        rgb=[int(color[i:i+2],16) for i in (1,3,5)]
        rgb=[min(255,round(v+(255-v)*.06)) if dark else round(v*.95) for v in rgb]
        color='#'+''.join(f'{v:02x}' for v in rgb)
    return color

def family(key):return SECTIONS.get(key,SECTIONS['personali'])[0]
