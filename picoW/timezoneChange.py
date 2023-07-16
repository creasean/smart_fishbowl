# This code was written by Juhyun Kim. 

import urequests

#기존 데이터 변경 날짜만 가져오기

#def timeOfSeoul() :
def dateOfSeoul() :
    # 시간정보 가져오기
    # print("\nQuerying the current GMT+0 time:")
    time_dict = urequests.get("http://date.jsontest.com")
    # print(time_dict.json())
    # print(time_dict.json()['date'])
    # print(time_dict.json()['milliseconds_since_epoch'])
    # print(time_dict.json()['time'])
    
    # UTC 기준으로 경과한 밀리초 계산
    milliseconds_since_epoch = int(time_dict.json()['milliseconds_since_epoch'])
    total_seconds = milliseconds_since_epoch // 1000
    total_minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)

    # UTC 시간대의 날짜와 시간 계산
    date_parts = time_dict.json()["date"].split("-")
    year = int(date_parts[2])
    month = int(date_parts[0])
    day = int(date_parts[1])
    is_pm = (time_dict.json()["time"][-2:] == "PM")
    hour = int(time_dict.json()["time"][:-9])
    if is_pm and hour != 12:
        hour += 12
    minute = int(time_dict.json()["time"][-8:-6])
    second = int(time_dict.json()["time"][-5:-3])

    # GMP+9 시간대의 시간 계산
    hour += 9 # 이 부분을 조정하면 다른 시간대로 변경 가능
    if hour >= 24:
        hour -= 24
        day += 1

    # 변환된 시간을 출력
    am_pm = "(AM)" if hour < 12 else "(PM)"
    hour = hour if hour <= 12 else hour - 12
    hour_str = str(hour) if hour >= 10 else "0" + str(hour)
    minute_str = str(minute) if minute >= 10 else "0" + str(minute)
    second_str = str(second) if second >= 10 else "0" + str(second)

    output_str = "{:04d}/{:02d}/{:02d}".format(year, month, day)
#원본    output_str = "{:02d}-{:02d}-{:04d} {}:{}:{} {}".format(month, day, year, hour_str, minute_str, second_str, am_pm)
    return(output_str)

#시간만 분리해서 가져오기
def timeOfSeoul() :
    # 시간정보 가져오기
    # print("\nQuerying the current GMT+0 time:")
    time_dict = urequests.get("http://date.jsontest.com")
    # print(time_dict.json())
    # print(time_dict.json()['date'])
    # print(time_dict.json()['milliseconds_since_epoch'])
    # print(time_dict.json()['time'])
    
    # UTC 기준으로 경과한 밀리초 계산
    milliseconds_since_epoch = int(time_dict.json()['milliseconds_since_epoch'])
    total_seconds = milliseconds_since_epoch // 1000
    total_minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)

    # UTC 시간대의 날짜와 시간 계산
    date_parts = time_dict.json()["date"].split("-")
    year = int(date_parts[2])
    month = int(date_parts[0])
    day = int(date_parts[1])
    is_pm = (time_dict.json()["time"][-2:] == "PM")
    hour = int(time_dict.json()["time"][:-9])
    if is_pm and hour != 12:
        hour += 12
    minute = int(time_dict.json()["time"][-8:-6])
    second = int(time_dict.json()["time"][-5:-3])

    # GMP+9 시간대의 시간 계산
    hour += 9 # 이 부분을 조정하면 다른 시간대로 변경 가능
    if hour >= 24:
        hour -= 24
        day += 1

    # 변환된 시간을 출력
    am_pm = "AM" if hour < 12 else "PM"
    hour = hour if hour <= 12 else hour - 12
    hour_str = str(hour) if hour >= 10 else "0" + str(hour)
    minute_str = str(minute) if minute >= 10 else "0" + str(minute)
    second_str = str(second) if second >= 10 else "0" + str(second)
    
    output_str = "{}{}:{}".format(am_pm, hour_str, minute_str)
#원본    output_str = "{} {}:{}:{}".format(am_pm, hour_str, minute_str, second_str)    
    
    return(output_str)


