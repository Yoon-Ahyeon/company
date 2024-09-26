import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from urllib.request import urlretrieve
import os

manual_df = pd.DataFrame([],columns=["board", "title", "date", "time", "view", "content", "comment"])
data_df = pd.DataFrame([],columns=["board", "title", "date", "time", "view", "content", "comment"]) 

# 게시글 본문 내용 크롤링
def collect_article_content():
    try:
        main_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div'))
        )
        return main_element.get_attribute('innerText')
    except:
        try:
            main_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div/div/div'))
            )
            return main_element.get_attribute('innerText')
        except:
            return None

driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options)

# 네이버 로그인 id, pwd
url='https://nid.naver.com/nidlogin.login'
id_ = 'ahyeon24'
pw = 'Heyho9209!'
    
driver.get(url)
driver.implicitly_wait(1)

# 네이버 login 
driver.execute_script("document.getElementsByName('id')[0].value=\'"+ id_ + "\'")
driver.execute_script("document.getElementsByName('pw')[0].value=\'"+ pw + "\'")
driver.find_element(by=By.XPATH,value='//*[@id="log.login"]').click()
time.sleep(1)

# 네이버 카페 url
baseurl='https://cafe.naver.com/skybluezw4rh/'
clubid = '29434212' # 네이버 카페 클럽 아이디 입력
# keyword = "%BB%FD%B1%E2%BA%CE" # 한국어는 인코딩된 주소로, 영어/숫자는 그대로
keyword = "ph365"

time.sleep(1)

# 네이버 페이지 개수 (크롤링할 페이지 개수)
num_page = 3

page = 0 # 현재 페이지 번호 초기화 (몇 번 page부터 뽑을건지 입력 가능)
index = 0 # 데이터프레임 인덱스 초기화

while page < num_page:

    driver.get("https://cafe.naver.com/ArticleSearchList.nhn?search.clubid="
               +str(clubid)
               + "&search.query=" 
               + str(keyword)
               +"&search.boardtype=L&search.totalCount=151&search.cafeId="+str(clubid)
               +"&search.page="+ str(page + 1))
    
    # iframe 변환 (네이버 카페는 게시물 내용이 iframe 안에 있음)
    driver.switch_to.frame("cafe_main")

    time.sleep(1) 
    driver.implicitly_wait(1)
   
    # BeautifulSoup으로 HTML을 파싱
    driver_page_source = driver.page_source
    soup = bs(driver_page_source, 'html.parser')

    # 해당 class를 가진 모든 게시글 링크들을 찾음
    article = soup.find_all(class_="inner_list")

    # 게시물 url, 번호 추출
    links = []
    post_num_list = []
    find_one = 0 # 첫 번째 'e'로 끝나는 ID를 찾았는지 확인하기 위한 변수
    for idx, link in enumerate(article):
         # 게시물의 고유 ID 추출
        idid = link.find(class_='article')['href'].split('articleid=')[-1]
        if idid[-1] == 'e':  # ID가 'e'로 끝나면
            if find_one == 0:  # 첫 번째 ID 발견 시 인덱스 저장
                find_idx = idx
                find_one += 10
            idid = idid.split('&')[0] # '&' 이전의 ID만 추출
        post_num_list.append(int(idid)) # 게시물 번호 리스트에 추가
        links.append(baseurl + idid) # 게시물 링크 리스트에 추가

    # HTML 테이블에서 데이터 추출
    wow_gongi = pd.read_html(driver_page_source)[0].iloc[[_ for _ in range(0,len(pd.read_html(driver_page_source)[0]),2)],[1,2,3,4]]
    wow_gongi = wow_gongi.reset_index(drop=True)
    wow_gongi.iloc[:,1] = wow_gongi.iloc[:,1].str.split('w').str[0]
    
    text_column = wow_gongi.columns # 열 이름 저장
    
    # 두 번째 테이블에서 데이터 추출
    wow = pd.read_html(driver_page_source)[find_idx+1].iloc[[_ for _ in range(0,len(pd.read_html(driver_page_source)[find_idx+1]),2)],[1,2,3,4]]
    wow = wow.reset_index(drop=True)
    wow.iloc[:,1] = wow.iloc[:,1].str.split('w').str[0]
    wow.columns = text_column
    
    # 두 개의 데이터프레임을 병합
    wow = pd.concat([wow_gongi, wow], axis=0)
    wow = pd.concat([wow.reset_index(drop=True), pd.DataFrame({'번호': post_num_list})], axis=1)
    wow = pd.concat([wow, pd.DataFrame({'링크': links})], axis=1) 
    
    # 게시글 하나씩 탐색
    idx_wow = 0
    while idx_wow < len(wow):
        print(page + 1, "번 페이지", idx_wow + 1, "번째 게시물")
        post_num = wow.iloc[idx_wow,4] # 게시물 번호
        print('글 번호:',post_num) 

        # 게시물 상세 페이지로 이동         
        driver.get(wow.iloc[idx_wow,5])
        driver.switch_to.frame("cafe_main")
        time.sleep(1)
        driver.implicitly_wait(1)
        
        # BeautifulSoup으로 HTML을 파싱
        another_soup = bs(driver.page_source, 'html.parser')

        # 해당 class를 가진 모든 게시글 링크들을 찾음
        another_article = another_soup.find_all(class_="inner_list")     

        # board name
        board =  driver.find_element(By.CLASS_NAME, "link_board").text
        
        # Title
        title = driver.find_element(By.CLASS_NAME, "title_text").text
        
        # contents
        contents = collect_article_content()

        # Date
        dates_text = driver.find_element(By.CLASS_NAME, "date").text
        dates, times = dates_text.split()

        # Views
        views_text = driver.find_element(By.CLASS_NAME, "count").text
        views = re.sub(r'\D', '', views_text)  

        # Comments
        comtemp_list = another_soup.find_all('span', {'class':'text_comment'})
        comment_1_list = []

        for idx in range(len(comtemp_list)):
            # 댓글 영역 찾기
            another_soup_find_all_div_class_comment_area = another_soup.find_all('div', {'class':'comment_area'})[idx]

            # 삭제된 댓글 처리
            if another_soup_find_all_div_class_comment_area.text.strip() == '삭제된 댓글입니다.':
                comment_1_list.append('Deleted')
                continue

            # 댓글 내용 추출      
            comment_span = another_soup_find_all_div_class_comment_area.find_all('span', {'class':'text_comment'})
    
            if comment_span:  # Check if comment_span is not empty
                comment = comment_span[0].text
                comment_1_list.append(comment)
            else:
                comment_1_list.append("No comment available")

        # 댓글이 없는 경우 처리
        if len(comtemp_list) == 0:
            comment_1_list.append("NO COMMENT")

        # 다음 게시물로 이동
        if idx_wow < len(wow) - 1:
            idx_wow += 1
        else:
            # 다음 게시물이 없으면, 다음 페이지로 이동
            print("ALL posts comsumed\nGO TO NEXT PAGE")
            page += 1 #
            idx_wow = 0            
            
            driver.get("https://cafe.naver.com/ArticleSearchList.nhn?search.clubid="
               +str(clubid)
               + "&search.query=" 
               + str(keyword)
               +"&search.boardtype=L&search.totalCount=151&search.cafeId="+str(clubid)
               +"&search.page="+ str(page + 1))

            driver.switch_to.frame("cafe_main")
    
            time.sleep(1)  # 페이지 로딩 시간
            driver.implicitly_wait(1)
            print(page + 1, " 번 페이지", idx_wow + 1, "번째 게시물")

            # BeautifulSoup으로 HTML을 파싱
            driver_page_source = driver.page_source
            soup = bs(driver_page_source, 'html.parser')

            # 해당 class를 가진 모든 게시글 링크들을 찾음
            article = soup.find_all(class_="inner_list")
            
            # 게시물 링크 및 번호 다시 추출
            links = []
            post_num_list = []
            find_one = 0
            for idx, link in enumerate(article):
                idid = link.find(class_='article')['href'].split('articleid=')[-1]
                if idid[-1] == 'e':
                    if find_one == 0:
                        find_idx = idx
                        find_one += 10
                    idid = idid.split('&')[0]
                post_num_list.append(int(idid))
                links.append(baseurl + idid)
            
            # 두 번째 테이블에서 데이터 추출
            wow = pd.read_html(driver_page_source)[1].iloc[[_ for _ in range(0,len(pd.read_html(driver_page_source)[1]),2)],[1,2,3,4]]
            wow = wow.reset_index(drop=True)
            wow.iloc[:,1] = wow.iloc[:,1].str.split('w').str[0]
            wow.columns = text_column
            wow = pd.concat([wow.reset_index(drop=True), pd.DataFrame({'번호': post_num_list})], axis=1)
            wow = pd.concat([wow, pd.DataFrame({'링크': links})], axis=1)

        # reply page 추적
        driver.get("https://cafe.naver.com/ArticleSearchList.nhn?search.clubid="
               +str(clubid)
               + "&search.query=" 
               + str(keyword)
               +"&search.boardtype=L&search.totalCount=151&search.cafeId="+str(clubid)
               +"&search.page="+ str(page + 1))
        
        driver.switch_to.frame("cafe_main")
        time.sleep(1)
        driver.implicitly_wait(1)

        # Reply Test (반복작업 아님)
        driver.get(wow.iloc[idx_wow,5])
        driver.switch_to.frame("cafe_main")
        driver.implicitly_wait(1)
        time.sleep(1)

        # dataframe으로 저장
        # 1번 저장 방법 - 수동 분석용
        if len(comment_1_list) == 0:
            comment_1_list = ["NO COMMENT"]  

        for comment in comment_1_list:
            new_row = {
                'board': board,   
                'title': title,
                'date': dates,    
                'time': times,
                'view': views, 
                'content': contents.replace('\n', ' ').replace('\r', ''), 
                'comment': comment   
            }
            manual_df = manual_df.append(new_row, ignore_index=True)  

        manual_df.to_csv(r"test_manual_analysis.csv", encoding="utf-8-sig", index=False)

        # 2번 저장 방법 - data 분석용
        if len(comment_1_list) == 0:
            comment_1_list = ["NO COMMENT"]  

        comments_string = "\n\n".join(comment_1_list)

        data_df.loc[index] = [
            board,    
            title,
            dates,   
            times, 
            contents.replace('\n', ' ').replace('\r', ''), 
            views,  
            comments_string 
        ]

        data_df.to_csv(r"test_data_analysis.csv", encoding="utf-8-sig", index=False)
        
        # print(board, title, dates, views, contents, comment_1_list)

        # main page에서 다음 페이지로 이동
        driver.get("https://cafe.naver.com/ArticleSearchList.nhn?search.clubid="
               +str(clubid)
               + "&search.query=" 
               + str(keyword)
               +"&search.boardtype=L&search.totalCount=151&search.cafeId="+str(clubid)
               +"&search.page="+ str(page + 1))
        
        driver.implicitly_wait(1)
        driver.switch_to.frame("cafe_main")
        time.sleep(1)
        index += 1
        if page >= num_page:
            break

