import pandas as pd
import re
from nltk.tokenize import word_tokenize
from nltk import ngrams
import nltk

nltk.download('punkt')

file_path = "test_240925.xlsx" # 크롤링된 내용이 저장되어 있는 filename (.py와 .xlsx 파일이 한 폴더 내에 함께 있어야함)
result_df = pd.read_excel(file_path)

# pd.concat 

content_series = result_df['comments']

def clean_text(x):
    return re.sub(r'\n', ' ', x).strip()

dt_pp = content_series.apply(clean_text)

pre_dt = dt_pp.str.replace(r'[^가-힣\s]', ' ', regex=True).str.strip()
pre_dt = pre_dt.str.split(expand=True).stack().reset_index(drop=True)
pre_dt = pre_dt[pre_dt != ""]

token_dt = pd.DataFrame({'word': pre_dt})

# 제거할 불용어 -> 분석에 들어가지 않도록 단어를 제거하는 것 (직접 설정하면 됨)
stop_words = set([
    "다시",
])

token_dt = token_dt[~token_dt['word'].isin(stop_words)]

token_counts = token_dt['word'].value_counts().reset_index(name='count')
token_counts.columns = ['word', 'count']

# 빈도 수 지정 (몇 번 이상 나온 단어만 저장)
token_counts = token_counts[token_counts['count'] >= 20]

# 파일로 저장
output_file_path = "token_counts.xlsx" 
token_counts.to_excel(output_file_path, index=False)

print(f"Token counts saved to {output_file_path}")