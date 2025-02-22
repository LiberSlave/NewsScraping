# 네이버 검색 API 예제 - 블로그 검색
import os
import sys
import urllib.request
from datetime import datetime
import urllib.parse
import json

client_id = "CFUWwL_4zSusIbCGXY7s"
client_secret = "35C9NdU7ZD"
encText = urllib.parse.quote("증시")
url = f"https://openapi.naver.com/v1/search/news?query={encText}&sort=date&display=10" # JSON 결과
# url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request) 
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    print(response_body.decode('utf-8'))
else:
    print("Error Code:" + rescode)