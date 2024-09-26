from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import openpyxl
import time
from urllib.request import urlretrieve
import os

# 본문 내용 수집 함수
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

# 제목 수집 함수
def collect_article_title():
    try:
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'title_text'))  # 게시글 제목 클래스 사용
        )
        return title_element.text
    except:
        return None

# 댓글 및 답글 수집 함수
def collect_comments_and_replies():
    comments = []
    replies = []
    try:
        # 댓글과 답글 요소를 수집
        comment_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.comment_area .text_comment'))
        )
        
        for comment in comment_elements:
            comment_text = comment.text
            
            # 댓글의 클래스 확인하여 답글인지 구분
            if "indent" in comment.get_attribute("class"):
                replies.append(comment_text)
            else:
                comments.append(comment_text)
                
        return comments, replies
    except Exception as e:
        print(f"Error collecting comments and replies: {e}")
        return None, None

    
# 크롬 드라이버 실행
driver = webdriver.Chrome()

url='https://nid.naver.com/nidlogin.login'
id_ = '' # 자신의 naver id (login할 때 필요)
pw = ''# 자신의 naver password (login할 때 필요)
    
driver.get(url)
driver.implicitly_wait(1)

# Naver login 네이버 로그인
driver.execute_script("document.getElementsByName('id')[0].value=\'"+ id_ + "\'")
driver.execute_script("document.getElementsByName('pw')[0].value=\'"+ pw + "\'")
driver.find_element(by=By.XPATH,value='//*[@id="log.login"]').click()
time.sleep(1)

# 여러 개의 URL 리스트
urls = [
    "example1", 
    "example2"
]  

# 결과를 저장할 데이터프레임 생성 (댓글과 답글 정보 포함)
all_data = pd.DataFrame(columns=['title', 'content', 'comments'])

for url in urls:
    driver.get(url)
    time.sleep(3)

    try:
        # iframe으로 전환
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "cafe_main"))
        )
        driver.switch_to.frame(element)

        # 제목, 본문, 댓글 및 답글 수집
        title = collect_article_title()
        all_text = collect_article_content()
        comments, replies = collect_comments_and_replies()

        if all_text:  # 본문 내용이 있을 경우
            all_data = all_data.append({
                'title': title,
                'content': all_text,
                'comments': ' | '.join(comments) if comments else 'No comments', # 행으로 변환해달라 or 줄바꿈
            }, ignore_index=True)

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        
# 파일명 설정
file_name = 'test_240925.xlsx'

# 새로운 파일로 저장 (덮어쓰기)
all_data.to_excel(file_name, index=False, engine='openpyxl')

# 크롬 드라이버 종료
driver.quit()