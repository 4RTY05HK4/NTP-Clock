from boot import i2c, adc, spi, clkPin, loadPin
from chars import indexes, digits5B
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
compensateTime = False

timer = Timer(0)


def handleInterrupt(timer):
    global interruptCounter
    interruptCounter = interruptCounter + 1


timer.init(period=1000, mode=Timer.PERIODIC, callback=handleInterrupt)


def secondTimer():
    global interruptCounter, seconds
    if interruptCounter > 0:
        state = disable_irq()
        interruptCounter = interruptCounter - 1
        enable_irq(state)
        seconds = seconds + 1


def serialByteWrite(data):
    clkPin.off()
    spi.write(data)


def displayWrite(adres, dana1, dana2, dana3, dana4):
    loadPin.off()
    serialByteWrite(bytes([adres]))
    serialByteWrite(bytes([dana1]))

    serialByteWrite(bytes([adres]))
    serialByteWrite(bytes([dana2]))

    serialByteWrite(bytes([adres]))
    serialByteWrite(bytes([dana3]))

    serialByteWrite(bytes([adres]))
    serialByteWrite(bytes([dana4]))
    loadPin.on()


def display_init_():
    displayWrite(0x0C, 0x00, 0x00, 0x00, 0x00)
    displayWrite(0x0F, 0x00, 0x00, 0x00, 0x00)
    displayWrite(0x0B, 0x07, 0x07, 0x07, 0x07)
    displayWrite(0x0A, 0x00, 0x00, 0x00, 0x00)
    displayWrite(0x09, 0x00, 0x00, 0x00, 0x00)
    displayWrite(0x0C, 0x01, 0x01, 0x01, 0x01)


def displayMatrx(matrx):
    for address in range(0, 8):
        displayWrite(
            address + 1,
            matrx[0][address],
            matrx[1][address],
            matrx[2][address],
            matrx[3][address],
        )


def displayWord(word, scroll):
    # word = "0123456789 :aąbcdefghijklłmnoprsśtuwxyz-,   16:56, piątek, 05-11-2021, 16:56"
    scroll_time_s = (
        0.01  # 0.050 for slow scroll // 0.03125 for 32FPS // 0.01667 for 60FPS
    )
    w, h = 8, 4
    targetMatrix = [[0 for x in range(w)] for y in range(h)]

    # print(targetMatrix)
    address = 0x00  # iterujemy do 8
    i = 1 << 8 - 1
    j = 0
    for d in range(0, len(word)):
        for column in range(0, 5):
            n = digits5B[indexes[word[d]]][column]

            while i > 0:

                if n & i:
                    targetMatrix[3][address] += 1
                else:
                    targetMatrix[3][address] += 0
                if n != 0x00 or indexes[word[d]] == 10:
                    targetMatrix[3][address] <<= 1
                    targetMatrix[2][address] <<= 1
                    targetMatrix[1][address] <<= 1
                    targetMatrix[0][address] <<= 1
                    if targetMatrix[3][address] >= 0x100:
                        targetMatrix[3][address] -= 0x100
                        targetMatrix[2][address] += 1
                    if targetMatrix[2][address] >= 0x100:
                        targetMatrix[2][address] -= 0x100
                        targetMatrix[1][address] += 1
                    if targetMatrix[1][address] >= 0x100:
                        targetMatrix[1][address] -= 0x100
                        targetMatrix[0][address] += 1
                    if targetMatrix[0][address] >= 0x100:
                        targetMatrix[0][address] -= 0x100

                i >>= 1
                address += 1

            if scroll == True:
                displayMatrx(targetMatrix)
                sleep(scroll_time_s)
            address = 0
            i = 1 << 8 - 1
        if indexes[word[d]] != 10:
            for addressTemp in range(0, 8):
                address = addressTemp
                targetMatrix[3][address] <<= 1
                targetMatrix[2][address] <<= 1
                targetMatrix[1][address] <<= 1
                targetMatrix[0][address] <<= 1
                if targetMatrix[3][address] >= 0x100:
                    targetMatrix[3][address] -= 0x100
                    targetMatrix[2][address] += 1
                if targetMatrix[2][address] >= 0x100:
                    targetMatrix[2][address] -= 0x100
                    targetMatrix[1][address] += 1
                if targetMatrix[1][address] >= 0x100:
                    targetMatrix[1][address] -= 0x100
                    targetMatrix[0][address] += 1
                if targetMatrix[0][address] >= 0x100:
                    targetMatrix[0][address] -= 0x100
        address = 0

        if scroll == True:
            displayMatrx(targetMatrix)
            sleep(scroll_time_s)
    if scroll == False:
        displayMatrx(targetMatrix)


def lightDetector():
    lightIntensity = adc.read()
    if lightIntensity > 50:
        displayWrite(0x0A, 0x06, 0x06, 0x06, 0x06)
    else:
        displayWrite(0x0A, 0x00, 0x00, 0x00, 0x00)


def getTimeAndDate():
    RTCaddr = i2c.scan()
    buf = bytearray(7)
    i2c.readfrom_mem_into(RTCaddr[0], 0x00, buf)
    return buf


def timeChange(flagaCzasZ, flagaCzasL):
    RTCaddr = i2c.scan()
    buf = bytearray(1)
    i2c.readfrom_mem_into(RTCaddr[0], 0x02, buf)
    if flagaCzasZ == True:
        i2c.writeto_mem(RTCaddr[0], 0x02, bytes([buf[0] - 1]))
    if flagaCzasL == True:
        i2c.writeto_mem(RTCaddr[0], 0x02, bytes([buf[0] + 1]))


def secondsCompensation():
    RTCaddr = i2c.scan()
    buf = bytearray(1)
    i2c.readfrom_mem_into(RTCaddr[0], 0x00, buf)
    bufTmp = int(hex(buf[0]).replace("0x", ""))
    if "59" in hex(buf[0]):
        i2c.writeto_mem(RTCaddr[0], 0x00, bytes([0]))
    elif "9" in hex(buf[0]):
        i2c.writeto_mem(RTCaddr[0], 0x00, bytes([buf[0] + 7]))
    else:
        i2c.writeto_mem(RTCaddr[0], 0x00, bytes([buf[0] + 1]))


def getTime():
    buff = getTimeAndDate()
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range(0, 7):
        tab[i] = int(hex(buff[i]).replace("0x", ""))
    return tab[2], tab[1], tab[0]


def getDate():
    global compensateTime
    buff = getTimeAndDate()
    str1 = ["", "", "", "", "", "", ""]
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range(0, 7):
        tab[i] = int(hex(buff[i]).replace("0x", ""))
        if tab[i] < 10 and i > 3:
            str1[i] = "0" + str(tab[i])
        else:
            str1[i] = str(tab[i])
        if i == 6:
            str1[i] = "20" + str(tab[i])
        if i == 3:
            if tab[i] == 1:
                str1[3] = "poniedziałek"
            elif tab[i] == 2:
                str1[3] = "wtorek"
            elif tab[i] == 3:
                str1[3] = "środa"
            elif tab[i] == 4:
                str1[3] = "czwartek"
            elif tab[i] == 5:
                str1[3] = "piątek"
            elif tab[i] == 6:
                str1[3] = "sobota"
                compensateTime = True
            elif tab[i] == 7:
                str1[3] = "niedziela"
                if compensateTime == True: 
                    secondsCompensation()  # compensating seconds 1spw (second per week)
                    compensateTime = False
    flagaCzasZ, flagaCzasL = False, False
    if tab[5] == 10 and tab[4] >= 25 and tab[3] == 7:
        flagaCzasZ = True
    if tab[5] == 3 and tab[4] >= 25 and tab[3] == 7:
        flagaCzasL = True
    date = str1[3] + ", " + str1[4] + "-" + str1[5] + "-" + str1[6] + "   "
    return date, flagaCzasZ, flagaCzasL


def getTimeNDateToString():
    buff = getTimeAndDate()
    str1 = ["", "", "", "", "", "", ""]
    tab = [0, 0, 0, 0, 0, 0, 0]
    for i in range(0, 7):
        tab[i] = int(hex(buff[i]).replace("0x", ""))
        if tab[i] < 10:
            str1[i] = "0" + str(tab[i])
        else:
            str1[i] = str(tab[i])
        if i == 6:
            str1[i] = "20" + str(tab[i])
    timeNdate = (
        str1[2]
        + ":"
        + str1[1]
        + ":"
        + str1[0]
        + ", "
        + str1[3]
        + ", "
        + str1[4]
        + "-"
        + str1[5]
        + "-"
        + str1[6]
    )
    return timeNdate


def clock_init_():
    h, m, seconds = getTime()
    if h < 10:
        hour = "0" + str(h)
    else:
        hour = str(h)
    if m < 10:
        minute = "0" + str(m)
    else:
        minute = str(m)
    time = " " + hour + ":" + minute
    displayWord(time, False)
    return h, m, seconds


def requestHandler(requestCode):
    if requestCode == 6:
        requestResponse = getTimeNDateToString()
    else:
        requestResponse = "AuthError"

    return requestResponse


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 80))
s.listen(5)


def handleConnectionRequests():
    station = network.WLAN(network.AP_IF)
    station.active(True)
    station.config(essid="NTPserver", hidden=True, authmode=4, password="pasz12port")
    station.ifconfig(
        ("192.168.137.25", "255.255.255.0", "192.168.137.1", "192.168.137.1")
    )
    # station.connect(ssid, password)
    while True:

        if station.isconnected() == True:
            conn, addr = s.accept()
            request = conn.recv(1024)
            request = str(request)
            requestCode = request.find("/?getTimeNDate")
            response = requestHandler(requestCode)
            conn.send("HTTP/1.1 200 OK\n")
            conn.send("Content-Type: text/html\n")
            conn.send("Connection: close\n\n")
            conn.sendall(response)
            conn.close()


display_init_()
lightDetector()
date, czasZimowy, czasLetni = getDate()
h, m, seconds = clock_init_()
# h, m, seconds = 23, 59, 55
# date, czasZimowy, czasLetni = "poniedziałek, 04-10-2021", False, False
_thread.start_new_thread(handleConnectionRequests, ())

while True:
    if seconds > 59:
        m = m + 1
        seconds = 0
    if m > 59:
        m = 0
        h = h + 1
    if h > 23:
        h = 0
        DateUpdateRequired = True
    if h == 0 and m == 2 and DateUpdateRequired == True:
        date, czasZimowy, czasLetni = getDate()
        h, m, seconds = getTime()  # time synchronization
        DateUpdateRequired = False
    if h == 2 and czasZimowy == True:
        h = h - 1
        timeChange(czasZimowy, czasLetni)
        czasZimowy = False
    if h == 2 and czasLetni == True:
        h = h + 1
        timeChange(czasZimowy, czasLetni)
        czasLetni = False
    if h < 10:
        hour = "0" + str(h)
    else:
        hour = str(h)
    if m < 10:
        minute = "0" + str(m)
    else:
        minute = str(m)
    time = " " + hour + ":" + minute
    if seconds % 9 == 0:
        checkLightIntesity = True
    if seconds % 10 == 0 and checkLightIntesity == True:
        lightDetector()
        checkLightIntesity = False
    if seconds == 0:
        if (h > 21 or h < 6) and m % 5 == 0:
            displayWord(date + time, True)
        elif h >= 6 and h <= 21:
            displayWord(date + time, True)
        displayWord(time, False)
    secondTimer()
