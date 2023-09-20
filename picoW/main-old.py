from machine import Pin, PWM, SoftI2C, ADC, reset
from time import sleep
from ssd1306 import SSD1306_I2C
from timezoneChange import *
import network
import urequests
import framebuf
from PicoDHT22 import PicoDHT22
import onewire, ds18x20
import random
import time
import json
import os

#나의 파이어 베이스 주소
firebase_url = "https://fishbowl-ac748-default-rtdb.firebaseio.com/"

# 저장 파일별 예시 자료 경로
firebase_path_DHT11_H = "/picoData/DHT11_H.json"
firebase_path_DHT11_T = "/picoData/DHT11_T.json"
firebase_path_onewire_T = "/picoData/WATER_T.json"
firebase_path_pcb_T = "/picoData/PCB_T.json"
firebase_path_water_level = "/picoData/WATER_LEVEL.json"
firebase_path_TimeStamp = "/picoData/TimeStamp.json"

#피코W에 부착되어 있는 LED 활용 선언
led = machine.Pin("LED", machine.Pin.OUT)
#서보모터 설정
servo1=PWM(Pin(0))
servo1.freq(50)
#부저 핀 설정
buzzer = PWM(Pin(22))
#ADC설정
adc=ADC(2)
#wifi setting
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
    buzzer.duty_u16(20000) # 100%=2^16, 따라서 50%
    buzzer.freq(800)
    sleep(0.2)
    buzzer.freq(1000)
    sleep(0.2)
    buzzer.freq(800)
    sleep(0.2)
    buzzer.duty_u16(0)

url = "https://fishbowl-ac748-default-rtdb.firebaseio.com/"
# DB 내역 가져오기위한 기초 설정

#디스플레이 표시를 위한 I2C세팅
i2c = SoftI2C(scl=Pin(10), sda=Pin(11))
display = SSD1306_I2C(128, 64, i2c, addr=0x3C)
sleep(0.5)

dht_sensor=PicoDHT22(Pin(17,Pin.IN,Pin.PULL_UP),dht11=True) # DHT11 온도 습도계 일체
data1=machine.Pin(16) # 실내온도 센서(고정형)  연결 번호 16, 수중 온도 27
data2=machine.Pin(27) # 수온 측정 온도 센서 연결 번호
temp_wire1=onewire.OneWire(data1)
temp_wire2=onewire.OneWire(data2)
temp_sensors1=ds18x20.DS18X20(temp_wire1)
temp_sensors2=ds18x20.DS18X20(temp_wire2)
roms1=temp_sensors1.scan()
roms2=temp_sensors2.scan()
print(len(roms1), 'temperature sensors found 1')
print(len(roms2), 'temperature sensors found 2')

def send_data(value, path):
    #함수 선언-입력한 값은 입력한 경로에 저장
    # Create a JSON payload with the value
    payload = '{"value": ' + str(value) + '}'
    # Send a PUT request to update the data in Firebase
    response = urequests.put(firebase_url + path, data=payload)
    print("Data sent to Firebase with response:", response.text)
    response.close()

def send_strdata(value, path):
    #함수 선언-입력한 값은 입력한 경로에 저장
    # Create a JSON payload with the value
    payload = json.dumps({"value": value})
    # Send a PUT request to update the data in Firebase
    response = urequests.put(firebase_url + path, data=payload)
    print("Data sent to Firebase with response:", response.text)
    response.close()


def setAngle(angle):
    global servo1
    a=int(((((angle+90)*2)/180)+0.5)/20*65535)
    servo1.duty_u16(a)

i=-180

while True:
#본격적인 피코 제어 파트
    try:

        response = urequests.get(firebase_url +".json").json()
        updatedTime = timeOfSeoul()

        # 현재 시간에서 시간과 분을 분리
        current_hour = int(updatedTime[11:13])
        current_minute = int(updatedTime[14:16])

        # 짝수 시간의 정각이 되면 시스템을 리부트
        if current_hour % 2 == 0 and current_minute == 0:
            # 실시간으로 확인된 각 객체 값을 딕셔너리에 넣기
            myobj = {
                'rebootedTime': updatedTime
                }
            urequests.patch(url+"RebootTime.json", json = myobj).json()
            print("reboot the system")
            time.sleep(1)
            machine.reset()

        if (updatedTime == "PM 10:45" ) : #피코 PCB의 LED가 켜지고 피딩 드럼이 반복적으로 회전(1분)
            led.on()
            
            while (i<180):
                setAngle(i)
                sleep(0.01)
                i=i+1
            
            while (i>-180):
                setAngle(i)
                sleep(0.01)
                i=i-1
            buzzer.duty_u16(20000) # 100%=2^16, 따라서 50%
            buzzer.freq(400)
            sleep(0.2)
            buzzer.freq(600)
            sleep(0.2)
            buzzer.freq(400)
            sleep(0.2)
            buzzer.duty_u16(0)
            sleep(1)
        else :
            led.off()

        T,H = dht_sensor.read() #DHT11 온도 센서 연결에 관한 코드
        value=adc.read_u16() #2^16, 0_65535 #ADC 세팅 수량계
        
        display.fill(0)
        display.show()
        display.text(updatedTime,0,0)
        display.text(str(T)+'C,',72,0)
        display.text(str(H)+'%',105,0)
        display.hline(0,10,128,5) # ---가--로--줄---
        
        display.text("Water T:",0,15)        
        for rom in roms2: #수중 온도 센서 온도 표시
            t2=temp_sensors2.read_temp(rom)
            print('{:>6.2f}'.format(t2), end=' ')
            display.text(str(round(t2,1))+'C',65,15)         
        print()
        display.hline(0,25,128,5) # ---가--로--줄---
        
        print("{}'C  {}%".format(T,H)) #공기 온도 습도 모니터링 표시
        print("T1 / T2 : ", end=' ')#온도표시
        temp_sensors1.convert_temp() #PCB 고정 온도계 온도 측정
        temp_sensors2.convert_temp() #수중 온도 센서 온도 측정
        time.sleep(0.5)

        display.text("Fixed T:",0,30)    
        for rom in roms1: #PCB 고정 온도계 온도 표시
            t1=temp_sensors1.read_temp(rom)
            print('{:>6.2f}'.format(t1), end=' ')
            display.text(str(round(t1,1))+'C',65,30)
        display.hline(0,40,128,5) # ---가--로--줄---
        
        if str(response['webInput']['DRUM_servo'])=="1":
            display.text("Food:"+"ON",0,45)
        else:           
            display.text("Food:"+"X",0,45)

        if str(response['webInput']['LIGHT_led'])=="1":
            display.text("Light:"+"ON",65,45)
        else:           
            display.text("Light:"+"X",65,45)        
        display.hline(0,55,128,5) # ---가--로--줄---

    #adc
        print("water level : ", end=' ')
        print(str(value))    
        
        if value>=35000:
            display.text('Water Lv: FULL',0,57)
        elif value>=30000:
            display.text('Water Lv: -1cm',0,57)
        elif value>=23000:
            display.text('Water Lv: -2cm',0,57)
        elif value>=18000:
            display.text('Water Lv: -3cm',0,57)
        elif value>=15000:
            display.text('Water Lv: -4cm',0,57)
        else:
            display.text('More Water PLZ',0,57)
        display.show()

    ### 파이어베이스로 센서 데이터 업로드
        send_data(T,firebase_path_DHT11_T) #DHT11에 일체된 온도계
        send_data(H,firebase_path_DHT11_H) #DHT11에 일체된 습도계
        send_data(round(t2,1),firebase_path_onewire_T) # 수중 온도계
        send_data(round(t1,1),firebase_path_pcb_T) #기판에 부착된 부품형 온도계
        send_data(value,firebase_path_water_level) #수량계(수심계)
        send_strdata(updatedTime,firebase_path_TimeStamp) #수량계(수심계)        
        sleep(1)
  
    except OSError as e:
        if e.args[0] in (103,104):
            print("Connection aborted. Rebooting Raspberry Pi Pico W...")
            time.sleep(1)
            machine.reset()
        else:
            print(f"Unexpected OSError: {e}")
            time.sleep(1)
            machine.reset()
            
        
    except:
        print("An error occurred. Rebooting Raspberry Pi Pico W...")
        time.sleep(1)
        machine.reset()
    




