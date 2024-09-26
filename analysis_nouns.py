import pandas as pd
import re
from konlpy.tag import Okt

# Load the data from test.xlsx
file_path = "test.xlsx"
result_df = pd.read_excel(file_path)

# Extract the 'content' column
content_series = result_df['content']

# Function to clean text
def clean_text(x):
    return re.sub(r'\n', ' ', x).strip()

# Apply clean_text function to the content column
dt_pp = content_series.apply(clean_text)

# Preprocess content: remove non-Korean characters
pre_dt = dt_pp.str.replace(r'[^가-힣\s]', ' ', regex=True).str.strip()
pre_dt = pre_dt[pre_dt != ""]  # Filter out empty strings

# Initialize the Okt tokenizer
okt = Okt()

# Function to extract nouns
def extract_nouns(text):
    return okt.nouns(text)

# Apply noun extraction to each content
nouns_list = pre_dt.apply(extract_nouns)

# Flatten the list of nouns
all_nouns = [noun for sublist in nouns_list for noun in sublist]

# Convert to a DataFrame
token_dt = pd.DataFrame({'word': all_nouns})

# Filter out unwanted words
stop_words = set([
])

# Filter tokens
token_dt = token_dt[~token_dt['word'].isin(stop_words)]

# # Count occurrences of tokens
# token_counts = token_dt['word'].value_counts().reset_index(name='count')
# token_counts.columns = ['word', 'count']

# # Filter results for tokens that appear at least 1 time
# token_counts = token_counts[token_counts['count'] >= 1]

# # Display the result
# print(token_counts)
