# NTP-Clock
## As the name suggests this is a clock with NTP server. It is based on ESP-32 platform and programmed in micropython. 

**What is this device for?**

> The basic principle of this project is to make use of ESP-32 and RTC module used in clocks, to provide a reliable source of time for every IoT device in home networks. 

**Why?**

> Most of IoT devices need internet connection to work properly, if for some reason they lose power, they will most likely lose time and date, causing them to lose ability to connect to internet and work properly. This device is supposed to help with that. 

**How?**
> The device has it's own RTC module with independent power source, which basically means, that it doesn't care if it still has power or not, time will go on. So when the power comes back it will show correct time and date, allowing other IoT devices to connect and synchronize date and time.

**Why not use atomic NTP servers to synchronize time and date?**
> Multiple reasons, with two most important.
> 1) Security, while communicating with the outside world there is a risk of being hacked or your data being stolen.
> 2) Because routers take significantly more time to start after a power outage.

## Now for technical part.

### For display I used four 8x8 LED matrix drived by MAX7219 and the RTC is DS3231.

The device is programmed with micropython, uses four 8x8 LED matrixes, DS3231 and have automatic display dimming controlled by a light sensitivity sensor made with photoresistor and built-in ADC.

![Schematic image](https://github.com/4RTY05HK4/NTP-Clock/blob/main/schematic.png)

## As of 4 October 2021 NTP functionality was added.
Using standard HTTP protocol the device is now able to provide time and date. Any other IoT device than wants to get that information shall connect to the device on given IP address with given GET method. To prevent the clock from not working properly, as it is primary function of the device, the NTP functionality, as well as managing Wi-Fi was moved to secondary thread. Device and newly added functionality was tested for critical errors and none were detected, however it requires more testing before submitting the final version.
