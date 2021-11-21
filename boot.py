
import machine
from chars import digits5B, indexes
from time import sleep
try:
  import usocket as socket
except:
  import socket
import network

data = 12   # pin connected to the serial input of the MAX7219 (DIN)
miso = 13   # pin for input from the SPI bus (not used here)
load = 14   # pin for loading data (CS)
clk  = 27   # pin for the clock of the serial link (CLK)
adcPin  = 33   # pin for the adc converter
sclPin = 25
sdaPin = 26

ssid = 'esp32-test'
password = 'pasz12port'

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
    displayWrite(0x0c,0x00,0x00,0x00,0x00)
    displayWrite(0x0f,0x00,0x00,0x00,0x00)
    displayWrite(0x0b,0x07,0x07,0x07,0x07)
    displayWrite(0x0a,0x00,0x00,0x00,0x00)
    displayWrite(0x09,0x00,0x00,0x00,0x00)
    displayWrite(0x0c,0x01,0x01,0x01,0x01)

def displayMatrx(matrx):
    for address in range (0,8):
        displayWrite(address+1, matrx[0][address], matrx[1][address], matrx[2][address], matrx[3][address])


def displayWord(word, scroll):
    #word = "0123456789 :aąbcdefghijklłmnoprsśtuwxyz-,   16:56, piątek, 05-11-2021, 16:56"
    scroll_time_s = 0.01 #0.050 for slow scroll // 0.03125 for 32FPS // 0.01667 for 60FPS
    w, h = 8, 4 
    targetMatrix = [[0 for x in range(w)] for y in range(h)]

    #print(targetMatrix)
    address = 0x00 #iterujemy do 8
    i = 1<<8-1
    j = 0
    for d in range(0,len(word)):
        for column in range(0,5):
            n = digits5B[indexes[word[d]]][column] 
            
            while i>0:

                if n & i:
                    targetMatrix[3][address] += 1
                else :
                    targetMatrix[3][address] += 0
                if n != 0x00 or indexes[word[d]] == 10:
                    targetMatrix[3][address] <<= 1
                    targetMatrix[2][address] <<= 1
                    targetMatrix[1][address] <<= 1
                    targetMatrix[0][address] <<= 1
                    if targetMatrix[3][address] >= 0x100 :
                        targetMatrix[3][address] -= 0x100
                        targetMatrix[2][address] += 1
                    if targetMatrix[2][address] >= 0x100 :
                        targetMatrix[2][address] -= 0x100
                        targetMatrix[1][address] += 1
                    if targetMatrix[1][address] >= 0x100 :
                        targetMatrix[1][address] -= 0x100
                        targetMatrix[0][address] += 1
                    if targetMatrix[0][address] >= 0x100 :
                        targetMatrix[0][address] -= 0x100

                i >>= 1
                address += 1


            if scroll == True : 
                displayMatrx(targetMatrix)
                sleep(scroll_time_s)
            address = 0    
            i = 1<<8-1
        if indexes[word[d]] != 10:
            for addressTemp in range(0,8):
                address=addressTemp
                targetMatrix[3][address] <<= 1
                targetMatrix[2][address] <<= 1
                targetMatrix[1][address] <<= 1
                targetMatrix[0][address] <<= 1
                if targetMatrix[3][address] >= 0x100 :
                    targetMatrix[3][address] -= 0x100
                    targetMatrix[2][address] += 1
                if targetMatrix[2][address] >= 0x100 :
                    targetMatrix[2][address] -= 0x100
                    targetMatrix[1][address] += 1
                if targetMatrix[1][address] >= 0x100 :
                    targetMatrix[1][address] -= 0x100
                    targetMatrix[0][address] += 1
                if targetMatrix[0][address] >= 0x100 :
                    targetMatrix[0][address] -= 0x100
        address = 0

        if scroll == True : 
            displayMatrx(targetMatrix)
            sleep(scroll_time_s)
    if scroll == False : displayMatrx(targetMatrix)

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

def secondsCompensation():
    RTCaddr = i2c.scan()
    buf = bytearray(1)
    i2c.readfrom_mem_into(RTCaddr[0], 0x00, buf)
    bufTmp = int(hex(buf[0]).replace('0x',''))
    if '59' in hex(buf[0]):
        i2c.writeto_mem(RTCaddr[0], 0x00, bytes([0]))
    elif '9' in hex(buf[0]):
        i2c.writeto_mem(RTCaddr[0], 0x00, bytes([buf[0]+7]))
    else:
        i2c.writeto_mem(RTCaddr[0], 0x00, bytes([buf[0]+1]))