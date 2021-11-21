
from boot import display_init_, displayWord, getTimeAndDate, lightDetector, timeChange, secondsCompensation
from time import sleep
from machine import Timer, disable_irq, enable_irq
import _thread

interruptCounter = 0
seconds = 0
h = 0
m = 0
date = ""
czasZimowy = False
czasLetni = False
DateUpdateRequired = False
checkLightIntesity = False

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
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range (0,7):
        tab[i] = int(hex(buff[i]).replace('0x',''))
    return tab[2], tab[1], tab[0]

def getDate():
    buff = getTimeAndDate()
    str1 = ['','','','','','','']
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range (0,7):
        tab[i] = int(hex(buff[i]).replace('0x',''))
        if tab[i] < 10 and i > 3 : str1[i] = "0" + str(tab[i])
        else : str1[i] = str(tab[i])
        if i == 6 : str1[i] = '20' + str(tab[i])
        if i == 3:
            if tab[i] == 1 : str1[3] = "poniedziałek"
            elif tab[i] == 2 : str1[3] = "wtorek"
            elif tab[i] == 3 : str1[3] = "środa"
            elif tab[i] == 4 : str1[3] = "czwartek"
            elif tab[i] == 5 : str1[3] = "piątek"
            elif tab[i] == 6 : str1[3] = "sobota"
            elif tab[i] == 7 : 
                str1[3] = "niedziela"
                secondsCompensation() # compensating seconds 1spw (second per week)
    flagaCzasZ, flagaCzasL = False, False
    if tab[5] == 10 and tab[4] >= 25 and tab[3] == 7 : flagaCzasZ = True
    if tab[5] == 3 and tab[4] >= 25 and tab[3] == 7 : flagaCzasL = True
    date = str1[3] + ", " + str1[4] + "-" + str1[5] + "-" + str1[6] + "   "
    return date, flagaCzasZ, flagaCzasL

def getTimeNDate():
    buff = getTimeAndDate()
    str1 = ['','','','','','','']
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range (0,7):
        tab[i] = int(hex(buff[i]).replace('0x',''))
        if tab[i] < 10: str1[i] = "0" + str(tab[i])
        else : str1[i] = str(tab[i])
        if i == 6 : str1[i] = '20' + str(tab[i])
    timeNdate = str1[2]+':'+str1[1]+':'+str1[0]+', '+str1[3]+', '+str1[4]+'-'+str1[5]+'-'+str1[6]
    return timeNdate

def clock_init_():
    h, m, seconds = getTime()
    if h < 10 : hour = '0' + str(h)
    else : hour = str(h)
    if m < 10 : minute = '0' + str(m)
    else : minute = str(m)
    time = ' ' + hour + ':' + minute
    displayWord(time, False)
    return h, m, seconds

def requestHandler(requestCode):
  if requestCode == 6:
    requestResponse = getTimeNDate()
  else:
    requestResponse = "AuthError"

  return requestResponse

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

def handleConnectionRequests():
    station = network.WLAN(network.AP_IF)
    station.active(True)
    station.config(essid='NTPserver', hidden=True, authmode=4, password='pasz12port')
    station.ifconfig(('192.168.137.25', '255.255.255.0', '192.168.137.1', '192.168.137.1'))
    #station.connect(ssid, password)
    while True:

        if station.isconnected() == True:
            conn, addr = s.accept()
            request = conn.recv(1024)
            request = str(request)
            requestCode = request.find('/?getTimeNDate')
            response = requestHandler(requestCode)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()

display_init_()
lightDetector()
h, m, seconds = clock_init_()
date, czasZimowy, czasLetni = getDate()
#h, m, seconds = 23, 59, 55
#date, czasZimowy, czasLetni = "poniedziałek, 04-10-2021", False, False
_thread.start_new_thread(handleConnectionRequests, ())

while True:
    if seconds > 59 : 
        m = m + 1
        seconds = 0
    if m > 59 : 
        m = 0
        h = h + 1
    if h > 23 : 
        h = 0
        DateUpdateRequired = True
    if h == 0 and m == 2 and DateUpdateRequired == True:
        date, czasZimowy, czasLetni = getDate() 
        h, m, seconds = getTime() # time synchronization
        DateUpdateRequired = False
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
    if seconds%9 == 0 : checkLightIntesity = True
    if seconds%10 == 0 and checkLightIntesity == True : 
        lightDetector()
        checkLightIntesity = False
    if seconds == 0 : 
        if (h > 21 or h < 6) and m%5 == 0 :
            displayWord(date+time, True)
        elif h >= 6 and h <=21 :
            displayWord(date+time, True)
        displayWord(time, False)
    secondTimer()

