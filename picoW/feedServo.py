from machine import Pin, PWM
from time import sleep
#서보모터 설정
servo1=PWM(Pin(0))
servo1.freq(50)

def setAngle(angle):
    global servo1
    a=int(((((angle+90)*2)/180)+0.5)/20*65535)
    servo1.duty_u16(a)
    
def feeding():
    i=-180
    setAngle(i)
    while (i<180):
        setAngle(i)
        sleep(0.01)
        i=i+1
    
    while (i>-180):
        setAngle(i)
        sleep(0.01)
        i=i-1
    
    
