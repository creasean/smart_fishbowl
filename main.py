from machine import SoftI2C, Pin, I2C, ADC, PWM
from ssd1306 import SSD1306_I2C
from time import sleep #
from timezoneChange import * #
import network #
import urequests #
import framebuf #
from PicoDHT22 import PicoDHT22
import utime
import machine
import time
import onewire, ds18x20
import random

#제어할 핀 설정
#추가 LED 설치시 25번 핀에 연결후 이용
#led = Pin(25, Pin.OUT)
#추가 장치 설치시 27번 핀에 연결후 이용
#device = Pin(27, Pin.OUT)
#나의 파이어 베이스 주소
firebase_url = "https://webtest02-b68f3-default-rtdb.firebaseio.com/"
# 저장 파일별 예시 자료 경로
firebase_path_DHT11_H = "/sensor_data/DHT11_H.json"
firebase_path_DHT11_T = "/sensor_data/DHT11_T.json"
firebase_path_onewire_T = "/sensor_data/onewire_T.json"
firebase_path_pcb_T = "/sensor_data/pcb_T.json"
firebase_path_water_level = "/sensor_data/water_level.json"

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

url = "https://webtest02-b68f3-default-rtdb.firebaseio.com/"
# DB 내역 가져오기위한 기초 설정
response = urequests.get(firebase_url +".json").json()
# byte형태의 데이터를 json으로 변경했기 때문에 메모리를 닫아주는 일을 하지 않아도 됨
# print(response)
# print(response['smartFarm'])
# print(response['smartFarm']['led'])


#디스플레이 표시를 위한 I2C세팅
i2c = SoftI2C(scl=Pin(10), sda=Pin(11))
display = SSD1306_I2C(128, 64, i2c, addr=0x3C)
sleep(1)

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


while True:
    
    # 현재 DB의 정보를 가져옴
    response = urequests.get(firebase_url +".json").json()
    # 현재 DB의 led 키 값의 상태에 따라 led 26번을 제어
    # 추후 홈페이지에서 값 입력시 피코로 전송 되는지 확인하기 위한 용도
    if (response['test_up_data']['pcb_LED'] >= 1) :
        led.on()
    else :
        led.off()

    print("pico LED : ", end=' ')
    print(str(response['test_up_data']['pcb_LED']))    

    updatedDate = dateOfSeoul()
    updatedTime = timeOfSeoul()

    T,H = dht_sensor.read() #DHT11 온도 센서 연결에 관한 코드

    value=adc.read_u16() #2^16, 0_65535 #ADC 세팅 수량계
    
    display.fill(0)
    display.show()
#    display.text("Time-",0,0)
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
#    display.text("AIR :",0,18)    
    print("{}'C  {}%".format(T,H)) #공기 온도 습도 모니터링 표시
   
    #온도표시
    print("T1 / T2 : ", end=' ')
    temp_sensors1.convert_temp() #PCB 고정 온도계 온도 측정
    temp_sensors2.convert_temp() #수중 온도 센서 온도 측정
    time.sleep(0.5)

    display.text("Fixed T:",0,30)    
    for rom in roms1: #PCB 고정 온도계 온도 표시
        t1=temp_sensors1.read_temp(rom)
        print('{:>6.2f}'.format(t1), end=' ')
        display.text(str(round(t1,1))+'C',65,30)

    display.hline(0,40,128,5) # ---가--로--줄---
    display.text("pcb_LED:"+str(response['test_up_data']['pcb_LED']),0,45)    


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
