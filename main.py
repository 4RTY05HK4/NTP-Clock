
from boot import display_init_, displayWord, getTimeAndDate, lightDetector, scrollDate, timeChange
from time import sleep
from machine import Timer, disable_irq, enable_irq
 
interruptCounter = 0
seconds = 0
h = 0
m = 0
date = ""
czasZimowy = False
czasLetni = False

timer = Timer(0)  
 
def handleInterrupt(timer):
  global interruptCounter
  interruptCounter = interruptCounter+1
 
timer.init(period=1000, mode=Timer.PERIODIC, callback=handleInterrupt)

def secondTimer():
    global interruptCounter, seconds
    if interruptCounter>0:
        state = disable_irq()
        interruptCounter = interruptCounter - 1
        enable_irq(state)
        seconds = seconds + 1

def getTime():
    buff = getTimeAndDate()
    str1 = ['','','','','','','',]
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range (0,7):
        tab[i] = int(hex(buff[i]).replace('0x',''))
        if i == 0 : seconds = tab[i]
        if i == 1 : m = tab[i]
        if i == 2 : h = tab[i]
    return tab[2], tab[1], tab[0]

def getDate():
    buff = getTimeAndDate()
    str1 = ['','','','','','','',]
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range (0,7):
        tab[i] = int(hex(buff[i]).replace('0x',''))
        if tab[i] < 10 and i > 3 : str1[i] = "0" + str(tab[i])
        else : str1[i] = str(tab[i])
        if i == 6 : str1[i] = '20' + str(tab[i])
        if tab[3] == 1 : str1[3] = "poniedziałek"
        elif tab[3] == 2 : str1[3] = "wtorek"
        elif tab[3] == 3 : str1[3] = "środa"
        elif tab[3] == 4 : str1[3] = "czwartek"
        elif tab[3] == 5 : str1[3] = "piątek"
        elif tab[3] == 6 : str1[3] = "sobota"
        elif tab[3] == 7 : str1[3] = "niedziela"
    flagaCzasZ, flagaCzasL = False, False
    if tab[5] == 10 and tab[4] >= 25 and tab[3] == 7 : flagaCzasZ = True
    if tab[5] == 3 and tab[4] >= 25 and tab[3] == 7 : flagaCzasL = True
    date = str1[3] + ", " + str1[4] + "-" + str1[5] + "-" + str1[6]
    return date, flagaCzasZ, flagaCzasL

def clock_init_():
    h, m, seconds = getTime()
    date = getDate()
    if h < 10 : hour = '0' + str(h)
    else : hour = str(h)
    if m < 10 : minute = '0' + str(m)
    else : minute = str(m)
    time = ' ' + hour + ':' + minute
    displayWord(time)
    return h, m, seconds

display_init_()
h, m, seconds = clock_init_()
date, czasZimowy, czasLetni = getDate()

while True:
    lightDetector()
    if seconds > 59 : 
        m = m + 1
        seconds = 0
    if m > 59 : 
        m = 0
        h = h + 1
    if h > 23 : 
        h = 0
        date, czasZimowy, czasLetni = getDate()
    if h == 2 and czasZimowy == True:
        h = h - 1
        timeChange(czasZimowy, czasLetni)
        czasZimowy = False
    if h == 2 and czasLetni == True:
        h = h + 1
        timeChange(czasZimowy, czasLetni)
        czasLetni = False
    if h < 10 : hour = '0' + str(h)
    else : hour = str(h)
    if m < 10 : minute = '0' + str(m)
    else : minute = str(m)
    time = ' ' + hour + ':' + minute
    if seconds == 0 : 
        scrollDate(date)
        displayWord(time)
    secondTimer()

