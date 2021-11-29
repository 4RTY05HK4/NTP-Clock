import machine
from chars import digits5B, indexes
from time import sleep

try:
    import usocket as socket
except:
    import socket
import network

data = 12  # pin connected to the serial input of the MAX7219 (DIN)
miso = 13  # pin for input from the SPI bus (not used here)
load = 14  # pin for loading data (CS)
clk = 27  # pin for the clock of the serial link (CLK)
adcPin = 33  # pin for the adc converter
sclPin = 25
sdaPin = 26

dataPin = machine.Pin(data, machine.Pin.OUT)
misoPin = machine.Pin(miso, machine.Pin.OUT)
loadPin = machine.Pin(load, machine.Pin.OUT)
clkPin = machine.Pin(clk, machine.Pin.OUT)

adc = machine.ADC(machine.Pin(adcPin))
adc.atten(machine.ADC.ATTN_11DB)
adc.width(machine.ADC.WIDTH_9BIT)

i2c = machine.SoftI2C(scl=machine.Pin(sclPin), sda=machine.Pin(sdaPin), freq=100000)

dataPin.off()
loadPin.off()
clkPin.off()

spi = machine.SoftSPI(
    baudrate=100000, polarity=0, phase=0, bits=8, sck=clkPin, mosi=dataPin, miso=misoPin
)
