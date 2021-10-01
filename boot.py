
import machine
from chars import digits5x8
from time import sleep

data = 12   # pin connected to the serial input of the MAX7219 (DIN)
miso = 13   # pin for input from the SPI bus (not used here)
load = 14   # pin for loading data (CS)
clk  = 27   # pin for the clock of the serial link (CLK)
adcPin  = 33   # pin for the adc converter
sclPin = 25
sdaPin = 26

dataPin = machine.Pin(data, machine.Pin.OUT)
misoPin = machine.Pin(miso, machine.Pin.OUT)
loadPin = machine.Pin(load, machine.Pin.OUT)
clkPin  = machine.Pin(clk, machine.Pin.OUT)

adc = machine.ADC(machine.Pin(adcPin))
adc.atten(machine.ADC.ATTN_11DB)
adc.width(machine.ADC.WIDTH_9BIT)

i2c = machine.SoftI2C(scl=machine.Pin(sclPin), sda=machine.Pin(sdaPin), freq=100000)

dataPin.off()
loadPin.off()
clkPin.off()
 
spi = machine.SoftSPI(baudrate=100000, polarity=0, phase=0, bits=8, sck = clkPin, mosi = dataPin, miso = misoPin)

def RTCgetAddr():
    global RTCaddr
    RTCaddr = i2c.scan()

def serialShiftByte(data): # zmienić nazwę
    clkPin.off()
    spi.write(data)

def serialWrite(address, data): # czy ta funkcja jest konieczna?
    buffer = bytearray(2)
    buffer[0] = address
    buffer[1] = data

    for i in range (0,4):
        loadPin.off()
        serialShiftByte(bytes([buffer[0]]))
        serialShiftByte(bytes([buffer[1]]))
        loadPin.on()
        loadPin.off()

def displayWrite(adres, dana1, dana2, dana3, dana4):
    loadPin.off()
    serialShiftByte(bytes([adres]))
    serialShiftByte(bytes([dana1]))
    
    serialShiftByte(bytes([adres]))
    serialShiftByte(bytes([dana2]))
    
    serialShiftByte(bytes([adres]))
    serialShiftByte(bytes([dana3]))
    
    serialShiftByte(bytes([adres]))
    serialShiftByte(bytes([dana4]))
    loadPin.on()

def display_init_():
    displayWrite(0x0c,0x00,0x00,0x00,0x00)
    displayWrite(0x0f,0x00,0x00,0x00,0x00)
    displayWrite(0x0b,0x07,0x07,0x07,0x07)
    displayWrite(0x0a,0x00,0x00,0x00,0x00)
    displayWrite(0x09,0x00,0x00,0x00,0x00)
    displayWrite(0x0c,0x01,0x01,0x01,0x01)

def display():
    dana = [0,0,0,0]
    for i in range (0,8):
        for j in range (0,4):
            dana[j] = digits5x8[j][i]
        displayWrite(i+1, dana[0], dana[1], dana[2], dana[3])

def displayMatrx(matrx):
    dana = [0,0,0,0]
    for i in range (0,8):
        for j in range (0,4):
            dana[j] = matrx[i][j]
        displayWrite(i+1, dana[0], dana[1], dana[2], dana[3])

def displayWord(slowo):
    dlugosc = len(slowo)
    tab = [0 for i in range(dlugosc)]
    w, h = 4, 8
    matrx = [[0 for x in range(w)] for y in range(h)]
    for i in range (0,8):
        for j in range (0,dlugosc):
            if slowo[j] == "0": tab[j] = digits5x8[0][i]
            elif slowo[j] == "1": tab[j] = digits5x8[1][i]
            elif slowo[j] == "2": tab[j] = digits5x8[2][i]
            elif slowo[j] == "3": tab[j] = digits5x8[3][i]
            elif slowo[j] == "4": tab[j] = digits5x8[4][i]
            elif slowo[j] == "5": tab[j] = digits5x8[5][i]
            elif slowo[j] == "6": tab[j] = digits5x8[6][i]
            elif slowo[j] == "7": tab[j] = digits5x8[7][i]
            elif slowo[j] == "8": tab[j] = digits5x8[8][i]
            elif slowo[j] == "9": tab[j] = digits5x8[9][i]
            elif slowo[j] == " ": tab[j] = digits5x8[10][i]
            elif slowo[j] == ":": tab[j] = digits5x8[11][i]
            elif slowo[j] == "a": tab[j] = digits5x8[12][i]
            elif slowo[j] == "ą": tab[j] = digits5x8[13][i]
            elif slowo[j] == "b": tab[j] = digits5x8[14][i]
            elif slowo[j] == "c": tab[j] = digits5x8[15][i]
            elif slowo[j] == "d": tab[j] = digits5x8[16][i]
            elif slowo[j] == "e": tab[j] = digits5x8[17][i]
            elif slowo[j] == "f": tab[j] = digits5x8[18][i]
            elif slowo[j] == "g": tab[j] = digits5x8[19][i]
            elif slowo[j] == "h": tab[j] = digits5x8[20][i]
            elif slowo[j] == "i": tab[j] = digits5x8[21][i]
            elif slowo[j] == "j": tab[j] = digits5x8[22][i]
            elif slowo[j] == "k": tab[j] = digits5x8[23][i]
            elif slowo[j] == "l": tab[j] = digits5x8[24][i]
            elif slowo[j] == "ł": tab[j] = digits5x8[25][i]
            elif slowo[j] == "m": tab[j] = digits5x8[26][i]
            elif slowo[j] == "n": tab[j] = digits5x8[27][i]
            elif slowo[j] == "o": tab[j] = digits5x8[28][i]
            elif slowo[j] == "p": tab[j] = digits5x8[29][i]
            elif slowo[j] == "r": tab[j] = digits5x8[30][i]
            elif slowo[j] == "s": tab[j] = digits5x8[31][i]
            elif slowo[j] == "ś": tab[j] = digits5x8[32][i]
            elif slowo[j] == "t": tab[j] = digits5x8[33][i]
            elif slowo[j] == "u": tab[j] = digits5x8[34][i]
            elif slowo[j] == "w": tab[j] = digits5x8[35][i]
            elif slowo[j] == "x": tab[j] = digits5x8[36][i]
            elif slowo[j] == "y": tab[j] = digits5x8[37][i]
            elif slowo[j] == "z": tab[j] = digits5x8[38][i]
            elif slowo[j] == "-": tab[j] = digits5x8[39][i]
            elif slowo[j] == ",": tab[j] = digits5x8[40][i]

        for k in range (0,4):
            if k == 0 : 
                matrx[i][k] = (tab[0] << 3) + (tab[1] >> 2)               
            elif k == 1 : 
                stab = str(hex(tab[1]<<6))
                if (tab[1]<<6) >= 0x100 :
                    if stab[2] == "7" : matrx[i][k] = (tab[1]<<6) - 0x700 + (tab[2] << 1) + (tab[3] >> 4)
                    elif stab[2] == "6" : matrx[i][k] = (tab[1]<<6) - 0x600 + (tab[2] << 1) + (tab[3] >> 4)
                    elif stab[2] == "5" : matrx[i][k] = (tab[1]<<6) - 0x500 + (tab[2] << 1) + (tab[3] >> 4)
                    elif stab[2] == "4" : matrx[i][k] = (tab[1]<<6) - 0x400 + (tab[2] << 1) + (tab[3] >> 4)
                    elif stab[2] == "3" : matrx[i][k] = (tab[1]<<6) - 0x300 + (tab[2] << 1) + (tab[3] >> 4)
                    elif stab[2] == "2" : matrx[i][k] = (tab[1]<<6) - 0x200 + (tab[2] << 1) + (tab[3] >> 4)
                    elif stab[2] == "1" : matrx[i][k] = (tab[1]<<6) - 0x100 + (tab[2] << 1) + (tab[3] >> 4)
                else : matrx[i][k] = (tab[1]<<6) + (tab[2] << 1) + (tab[3] >> 4)
            elif k == 2 : 
                if (tab[3] << 4) >= 256 : matrx[i][k] = (tab[3] << 4) - 256 + (tab[4] >> 1)
                else : matrx[i][k] = (tab[3] << 4) + (tab[4] >> 1)
            elif k == 3 : 
                stab = str(hex(tab[4]<<7))
                if (tab[4]<<7) >= 0x100 :
                    if stab[2] == 'f' : matrx[i][k] = (tab[4]<<7) - 0xf00 + (tab[5] << 2)
                    elif stab[2] == 'e' : matrx[i][k] = (tab[4]<<7) - 0xe00 + (tab[5] << 2)
                    elif stab[2] == 'd' : matrx[i][k] = (tab[4]<<7) - 0xd00 + (tab[5] << 2)
                    elif stab[2] == 'c' : matrx[i][k] = (tab[4]<<7) - 0xc00 + (tab[5] << 2)
                    elif stab[2] == 'b' : matrx[i][k] = (tab[4]<<7) - 0xb00 + (tab[5] << 2)
                    elif stab[2] == 'a' : matrx[i][k] = (tab[4]<<7) - 0xa00 + (tab[5] << 2)
                    elif stab[2] == '9' : matrx[i][k] = (tab[4]<<7) - 0x900 + (tab[5] << 2)
                    elif stab[2] == '8' : matrx[i][k] = (tab[4]<<7) - 0x800 + (tab[5] << 2)
                    elif stab[2] == '7' : matrx[i][k] = (tab[4]<<7) - 0x700 + (tab[5] << 2)
                    elif stab[2] == '6' : matrx[i][k] = (tab[4]<<7) - 0x600 + (tab[5] << 2)
                    elif stab[2] == '5' : matrx[i][k] = (tab[4]<<7) - 0x500 + (tab[5] << 2)
                    elif stab[2] == '4' : matrx[i][k] = (tab[4]<<7) - 0x400 + (tab[5] << 2)
                    elif stab[2] == '3' : matrx[i][k] = (tab[4]<<7) - 0x300 + (tab[5] << 2)
                    elif stab[2] == '2' : matrx[i][k] = (tab[4]<<7) - 0x200 + (tab[5] << 2)
                    elif stab[2] == '1' : matrx[i][k] = (tab[4]<<7) - 0x100 + (tab[5] << 2)
                else : matrx[i][k] = (tab[4]<<7) + (tab[5] << 2)
    displayMatrx(matrx)

def scrollDate(slowo):

    for j in range(0,2):

        word = slowo

        scrolledWord = "      "

        word = word+scrolledWord

        listedWord = list(word)
        listedScrolledWord = list(scrolledWord)

        for i in range(0, len(word)):
            listedScrolledWord[0] = listedScrolledWord[1]
            listedScrolledWord[1] = listedScrolledWord[2]
            listedScrolledWord[2] = listedScrolledWord[3]
            listedScrolledWord[3] = listedScrolledWord[4]
            listedScrolledWord[4] = listedScrolledWord[5]
            listedScrolledWord[5] = listedWord[i]
            
            scrolledWord = "".join(listedScrolledWord)
            displayWord(scrolledWord)
            if i >= len(word)-12 : sleep(0.1)
            #sleep(0.1)

def lightDetector():
    lightIntensity = adc.read()
    if lightIntensity > 50 : displayWrite(0x0a,0x06,0x06,0x06,0x06)
    else : displayWrite(0x0a,0x00,0x00,0x00,0x00)

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
        i2c.writeto_mem(RTCaddr[0], 0x02, bytes([buf[0]-1]))
    if flagaCzasL == True:
        i2c.writeto_mem(RTCaddr[0], 0x02, bytes([buf[0]+1]))