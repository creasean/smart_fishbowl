import gc
from machine import Pin, PWM, SoftI2C, ADC, reset
from time import sleep
from timezoneChange import *
from feedServo import *
import network
import urequests
#import framebuf
from PicoDHT22 import PicoDHT22
import onewire, ds18x20
#import random
import time
import json
import os

airTemp=0
airHumid=0
pcbTemp=0
waterTemp=0
#waterLevel=0

#ADC설정
adc=ADC(2)

dht_sensor=PicoDHT22(Pin(17,Pin.IN,Pin.PULL_UP),dht11=True) # DHT11 온도 습도계 일체
temp_sensors1=ds18x20.DS18X20(onewire.OneWire(machine.Pin(16))) #기판 고정칩 pin 16
temp_sensors2=ds18x20.DS18X20(onewire.OneWire(machine.Pin(27))) #수중 온도 측정 센서 pin 27
#roms1=temp_sensors1.scan()
#roms2=temp_sensors2.scan()

SSID = "iptime-home"       # 공유기의 SSID를 따옴표 안에 넣으세요.
password = "js4u2014"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    # 와이파이 연결하기
    wlan.connect(SSID, password)  # 12, 13번 줄에 입력한 SSID와 password가 입력됨
    print("Waiting for Wi-Fi connection", end="...") #쉘에 보여주기 위한 문자
    print()
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
else:
    print(wlan.ifconfig())
    print("WiFi is Connected")
    print()
    
url ="https://sfb-optimization-default-rtdb.firebaseio.com/"

#from timezoneChange import timeOfSeoul
updatedTime = timeOfSeoul()
updatedDate = dateOfSeoul()
#print(type(updatedTime)) #str
#print(updatedTime)

updataInitialize={
    'airTemp':0,
    'airHumid':0,
    'pcbTemp':0,
    'waterTemp':0
    #,'waterLevel':0
    }
controldataInitialize={
    'led':1,
    'feed':1
    }

urequests.patch(url+"SmartFishBowl.json", json = updataInitialize).json()
urequests.patch(url+"SmartFishBowl.json", json = controldataInitialize).json()
print("SmartFishBowl has been initialized.")

response = urequests.get(url+".json").json()
#print(response) #응답을 받아봄
#print(response['SmartFishBowl'])

  
while True:
    try:
        updatedTime = timeOfSeoul()
        #print(updatedTime[3:5],":", updatedTime[6:8]) #시간 확인해 보기
        current_hour = int(updatedTime[3:5])
        current_minute = int(updatedTime[6:8])

        # 짝수 시간의 정각이 되면 시스템을 리부트                
        if current_hour % 2 == 0 and current_minute == 00:
                # 실시간으로 확인된 각 객체 값을 딕셔너리에 넣기
            rebootT = {
                'rebootedTime': updatedDate+" "+updatedTime
                }
            urequests.patch(url+"SmartFishBowl.json", json = rebootT).json()
                          
            print("reboot the system")
            time.sleep(1)
            machine.reset()
            
        if current_hour == 07 and current_minute == 00:
                # 실시간으로 확인된 각 객체 값을 딕셔너리에 넣기
            print("\n피딩 드럼 회전")
            feeding()
            feedTime = {
                'lastFeeding': updatedDate+" "+updatedTime
                }
            urequests.patch(url+"SmartFishBowl.json", json = feedTime).json()
            time.sleep(1)
                
        # 현재 DB의 정보를 가져옴
        response = urequests.get(url+".json").json() # RTDB 데이터 가져오기
        T,H = dht_sensor.read() #DHT11 온도 센서 연결에 관한 코드
        
        temp_sensors1.convert_temp() #PCB 고정 온도계 온도 재측정
        temp_sensors2.convert_temp() #수중 온도 센서 온도 재측정
        
        for rom in temp_sensors1.scan(): #PCB 고정 온도계 온도 표시
            t1=round(temp_sensors1.read_temp(rom),1)
        for rom in temp_sensors2.scan(): #t 수중온도 
            t2=round(temp_sensors2.read_temp(rom),1)        

        value={
            'airTemp':T,
            'airHumid':H,
            'pcbTemp':t1,
            'waterTemp':t2
            #,'waterLevel':random.randrange(301, 400)
            }
        urequests.patch(url+"SmartFishBowl.json", json=value).json()
        Time_value={
            'timeStamp':updatedTime
            }
        urequests.patch(url+"SmartFishBowl.json", json=Time_value).json()

        ''' #추후 서버의 값을 읽어서 자동 먹이 공급기와 조명을 켜고 끄는 데 이용
        print("------------------")
        if (response['SmartFishBowl']['led'] == 1) :
            led.value(1)
            print("led ON")        
        else :
            led.value(0)
            print("led OFF")                
            # 현재 DB의 servo 키 값의 상태에 따라 led 27번을 제어
        if (response['SmartFishBowl']['feed'] == 1) :
            feed.value(1)
            print("feeding ON")        
        else :
            feed.value(0)
            print("feeding OFF")
        '''
        
        print("\n현재 서버에 저장되어 있는 값")
        print(response['SmartFishBowl'])

        gc.collect()
        
        
    except OSError as e:
        if e.args[0] in (103,104):
            print("Connection aborted. Rebooting Raspberry Pi Pico W...")
            time.sleep(1)
            machine.reset()
        else:
            print(f"Unexpected OSError: {e}")
            time.sleep(1)
            machine.reset()
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(1)
        machine.reset()
    except:
        print("An error occurred. Rebooting Raspberry Pi Pico W...")
        time.sleep(1)
        machine.reset()
        
