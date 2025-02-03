import os
import sys
import urllib.request
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import winsound

client_id = "CFUWwL_4zSusIbCGXY7s"
client_secret = "35C9NdU7ZD"


keyword='특징주'
keyword2='최두선'
encText = urllib.parse.quote("박연오 기자")


# url로부터 네이버 api에서 데이터를 받아오는 함수
def check_keyword1():

    url1 = "https://www.financialpost.co.kr/" # JSON 결과
    response1 = requests.get(url1)

    response1.encoding = 'utf-8'
    soup1=response1.text

    # print(soup)

    # soup 내용을 메모장에 저장
    # with open('soup_text.txt', 'w', encoding='utf-8') as file:
    #  file.write(soup1)

    count1 = soup1.count(keyword)
    print(response1, count1)

    if count1 !=2:
        return True
    return False




def job():
    # 현재시각 출력
    now=datetime.now()
    print(now.hour,now.minute, now.second)

    TorF1 = check_keyword1()
    print(TorF1)



    if TorF1:
        winsound.Beep(500,500)
        print('파이낸셜포스트')
        sys.exit()  # 프로그램 종료



schedule.every(5).seconds.do(job)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Ctrl+C에 의해 프로그램이 중지되었습니다.")