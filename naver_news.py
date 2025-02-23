# 네이버 검색 API 예제 - 블로그 검색
import urllib.request
from datetime import datetime
import urllib.parse
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
import pandas as pd

# API 응답 pubDate의 포맷
API_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
INPUT_DATE_FORMAT = "%Y%m%d %H:%M"

def get_news_in_range(query, start_time_str=None, end_time_str=None, sort='date', display=100, start=1):
    """
    get_naver_news 함수를 반복 호출하여, 
    start 인수를 100, 200, 300… 늘려가면서 뉴스 기사들을 수집한 후,
    수집한 기사 중에서 pubDate가 사용자가 원하는 시간 구간([start_time, end_time])에 해당하는 기사들만 반환합니다.
    
    단, start 인수는 최대 1000까지 허용됩니다.
    
    Parameters:
        query (str): 검색어
        start_time_str (str): 원하는 시작 시간 (예: "Thu, 20 Feb 2025 10:31:00 +0900")
        end_time_str (str): 원하는 종료 시간 (예: "Thu, 20 Feb 2025 10:50:00 +0900")
        sort (str): 정렬 기준 (기본 'date')
        display (int): 한 번 호출 시 반환할 기사 수 (최대 100)
        start (int): 첫 호출 시 시작 인덱스 (기본 1)
        
    Returns:
        list: 시간 구간에 해당하는 기사 항목들의 리스트
    """

    # [수정된 부분] 사용자 입력값은 INPUT_DATE_FORMAT을 사용하여 파싱하고, KST (UTC+9) 타임존을 지정합니다.
    KST = timezone(timedelta(hours=9))

    # [수정된 부분] start_time_str, end_time_str이 None인 경우, 매우 넓은 시간 범위로 설정
    if start_time_str is not None:
        start_time_dt = datetime.strptime(start_time_str, INPUT_DATE_FORMAT).replace(tzinfo=KST)
    else:
        # 아주 오래된 날짜로 설정 (예: 1970-01-01)
        start_time_dt = datetime(1970, 1, 1, tzinfo=KST)
    
    if end_time_str is not None:
        end_time_dt = datetime.strptime(end_time_str, INPUT_DATE_FORMAT).replace(tzinfo=KST)
    else:
        # 아주 미래의 날짜로 설정 (예: 3000-01-01)
        end_time_dt = datetime(3000, 1, 1, tzinfo=KST)
    
    collected_items = []
    current_start = start
    
    while current_start <= 1000:
        # get_naver_news 함수는 이미 정의되어 있다고 가정합니다.
        news_data = get_naver_news(query, sort, display, current_start)
        if not news_data or 'items' not in news_data:
            break
        
        items = news_data['items']
        if not items:
            break
        
        # 이번 호출의 모든 기사를 수집
        collected_items.extend(items)
        
        # 이번 호출에서 가장 오래된(마지막) 기사 pubDate를 확인합니다.
        last_item_pubDate_str = items[-1].get('pubDate')
        last_item_pubDate = datetime.strptime(last_item_pubDate_str, API_DATE_FORMAT)
        
        # 만약 가장 오래된 기사가 원하는 시작 시간보다 이전(더 오래됨)이라면,
        # 이후 기사는 모두 원하는 구간 외일 것이므로 반복을 종료합니다.
        if last_item_pubDate <= start_time_dt:
            break
        
        current_start += display

    # 수집한 기사들 중에서 pubDate가 [start_time, end_time] 구간에 있는 기사만 필터링
    filtered_items = []
    for item in collected_items:
        pubDate_str = item.get('pubDate')
        if pubDate_str:
            pubDate_dt = datetime.strptime(pubDate_str, API_DATE_FORMAT)
            if start_time_dt <= pubDate_dt <= end_time_dt:
                filtered_items.append(item)
    
    print("뉴스 기사의 수:", len(filtered_items))
                
    return filtered_items







def get_naver_news(query, sort='date', display=100, start=1):
    """
    네이버 뉴스 API를 호출하여 검색 결과를 JSON 형식으로 반환합니다.
    
    Parameters:
        query (str): 검색어 (예: "한한령")
        sort_order (str): 정렬 기준 ("date" 또는 "sim")
        display (int): 한 번 호출 시 반환할 기사 수 (최대 100)
        start (int): 검색 시작 위치 (최대 1000까지 가능)
        
    Returns:
        dict: 네이버 뉴스 API의 JSON 응답 결과
    """
    client_id = "CFUWwL_4zSusIbCGXY7s"
    client_secret = "35C9NdU7ZD"
    # 검색어 URL 인코딩
    encText = urllib.parse.quote(query)
    # API URL 구성
    url = f"https://openapi.naver.com/v1/search/news?query={encText}&sort={sort}&display={display}&start={start}"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    
    if rescode == 200:
        response_body = response.read()
    else:
        print("Error Code:" + str(rescode))
        return None
    
    # JSON 디코딩 후 결과 반환
    response_result = json.loads(response_body.decode('utf-8'))
    return response_result



def prepro_naver_news(response_result):
    df = pd.DataFrame(response_result)
    # API에서 받은 형식: "Sun, 23 Feb 2025 12:00:00 +0900"
    df['pubDate'] = pd.to_datetime(df['pubDate'], format="%a, %d %b %Y %H:%M:%S %z")

    # tzinfo(타임존) 정보를 제거하여 naive datetime 객체로 만듦
    df['pubDate'] = df['pubDate'].dt.tz_localize(None)
    return df




def save_naver_news(df):
    """
    DataFrame(df)을 MySQL 데이터베이스의 naver_news 테이블에 저장합니다.
    
    Parameters:
        df (DataFrame): 저장할 데이터프레임
    """
    username = 'root'
    password = '219423'
    host = 'localhost'
    port = '3306'
    database = 'trading'

    # SQLAlchemy 엔진 생성 (mysql+pymysql 사용)
    engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")
    
    # DataFrame을 naver_news 테이블에 저장 (중복 키 무시)
    df.to_sql('naver_news', con=engine, if_exists='append', index=False, method=insert_ignore)
    
    print("DataFrame이 MySQL에 저장되었습니다.")

def insert_ignore(table, conn, keys, data_iter):
    from sqlalchemy.dialects.mysql import insert
    # data_iter는 DataFrame의 각 행 데이터가 튜플로 들어옵니다.
    data = [dict(zip(keys, row)) for row in data_iter]
    # SQLAlchemy insert 객체를 만들고, MySQL 전용 prefix "IGNORE"를 추가합니다.
    stmt = insert(table.table).prefix_with("IGNORE")
    conn.execute(stmt, data)
