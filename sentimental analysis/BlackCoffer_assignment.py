#!/usr/bin/env python
# coding: utf-8

# In[1]:


## Run the the code as per the steps Sequence


# ### Step1: import Python libreries

# In[2]:


import pandas as pd 
import requests
from bs4 import BeautifulSoup
import os
import nltk
nltk.download('punkt')


# ### Step 2: Read input Excel

# In[3]:


df=pd.read_excel('Input.xlsx')


# In[4]:


df


# # Data Extraction

# ### Step 3: Creat folder to save extracted fiels

# In[5]:


output_directory = "Extracted_Articles"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


# ### Step 4: User defiend funtion Extract the text from the webpage 

# In[6]:


def extract_article_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title').get_text()
        article_text = ""
        article_content = soup.find('div', class_='td-post-content tagdiv-type')
        if article_content == None:
            article_content = soup.find('div', class_='td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type')
        if article_content:
            headings = [heading.get_text() for heading in article_content.find_all('h2')]
            paragraphs = [paragraph.get_text() for paragraph in article_content.find_all('p')]
            points=[point.get_text() for point in article_content.find_all('li') ]
            article_text = "\n".join(headings) + "\n" + "\n".join(paragraphs) + "\n" + "\n".join(points)
        return title, article_text
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        return None, None


# ### Step 5:Save the Extracted texts in the text files

# In[7]:


for index, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    
    title, article_text = extract_article_text(url)

    if title and article_text:
        output_filename = os.path.join(output_directory, f"{url_id}.txt")
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(f"Title: {title}\n\n")
            file.write(article_text)

        print(f"Article extracted from {url} and saved as {output_filename}")
    else:
        print(f"Failed to extract article from {url}")

print("Extraction completed.")


# # Data Analysis
# ## Sentimental Analysis

# In[8]:


### Step 6: User defind functions for data analysis


# In[9]:


import os
from nltk.tokenize import word_tokenize
import re

# Function to load stop words from a folder 
def load_stop_words_from_files(folder_path):
    stop_words = set()  # Use a set to avoid duplicate stop words
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='latin-1') as file:
            stop_words.update([word.strip() for word in file.readlines()])
    return stop_words
##def load_stop_words(file_path):
 ##   with open(file_path, 'r', encoding='latin-1') as file:
   ##     stop_words = file.readlines()
   ## return [word.strip() for word in stop_words]

# Function to load text from a file
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Function to clean the text using stop words
def clean_text(text, stop_words):
    # Tokenize the text into words
    words = word_tokenize(text)
    
    # Initialize a list to store cleaned words
    cleaned_words = []
    
    # Iterate through the words in the text
    for word in words:
        # Check if the word is not in the stop words list
        if word.lower() not in stop_words:
            # Keep the word in the cleaned text
            cleaned_words.append(word)
    
    # Join the cleaned words back into a single string
    cleaned_text = ' '.join(cleaned_words)
    
    return cleaned_text
def load_positive_words(folder_path):
    positive_words = set()  # Use a set to avoid duplicate stop words
    for file_name in os.listdir(folder_path):
        if file_name == 'positive-words.txt':
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='latin-1') as file:
                positive_words.update([word.strip() for word in file.readlines()])
    return positive_words
def load_negitive_words(folder_path):
    negitive_words = set()
    for file_name in os.listdir(folder_path):         
        if file_name == 'negative-words.txt':
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='latin-1') as file:
                negitive_words.update([word.strip() for word in file.readlines()])        
    return negitive_words
def count_syllables(word):
    vowels = 'aeiouy'
    word = word.lower()
    count = 0
    for index, letter in enumerate(word):
        # Count vowel if current letter is a vowel and not preceded by another vowel
        if letter in vowels and (index == 0 or word[index - 1] not in vowels):
            count += 1
    
    # Handle exceptions
        if word.endswith('es') or word.endswith('ed'):
            count -= 1
        if word.endswith('e') and not word.endswith('le'):
            count -= 1
        if count == 0:  # Ensure at least one syllable
            count = 1
    
    return count

def calculate_fog_index(text):
    # Count words and sentences
    words = re.findall(r'\w+', text)
    num_words = len(words)
    sentences = re.split(r'[.!?]', text)
    num_sentences = len(sentences)

    # Calculate average sentence length
    average_sentence_length = num_words / num_sentences

    # Identify complex words
    complex_words = [word for word in words if count_syllables(word) > 2]
    num_complex_words = len(complex_words)
    percentage_complex_words = num_complex_words / num_words * 100

    # Calculate Fog Index
    fog_index = 0.4 * (average_sentence_length + percentage_complex_words)

    return fog_index
def count_personal_pronouns(text):
    # Define the regex pattern to match personal pronouns
    pattern = r'\b(I|we|my|ours|us)\b'

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    # Initialize count
    count = 0

    # Iterate through the matches and increment count
    for match in matches:
        # Check if the match is not "US" (country name)
        if match != "US":
            count += 1

    return count
def Average_Word_Length (text):
    ## splict the word
    words = re.findall(r'\w+', text)
    # Calucate chatected in the each word 
    total_characters = sum(len(word) for word in words)
    total_words = len(words)
    if  len(words) > 0:
        average_length = total_characters / total_words
    else:
        average_length = 0  # Avoid division by zero error if there are no words
    
    return average_length




# In[10]:


### Step 7: Userdefied fundtion for creating output data struction file 


# In[11]:


def Sentiment_analysis(text_files_folder,stop_words_folder,folder_path):
    # Load positive & Negivitive words from all files in the folder
    positive_words = load_positive_words(folder_path)
    negitive_words = load_negitive_words(folder_path)
    # Load stop words from all files in the folder
    stop_words = load_stop_words_from_files(stop_words_folder)
    for file_name in os.listdir(text_files_folder):
        category = file_name.split('.')[0]  # Extract category from file name
        file_path = os.path.join(text_files_folder, file_name)
        text = load_text(file_path)
        # Clean the text using stop words for the corresponding webpage 
        cleaned_text = clean_text(text, stop_words)
        cleaned_words = re.findall(r'\w+',cleaned_text)
        # Caluclate the Positive and Negivitive score
        nw =[]
        for word in negitive_words:
            if word in cleaned_words:
                    nw.append(word)    
        Negative_Score = len(nw)
        pw =[]
        for word in positive_words:
            if word in cleaned_words:
                pw.append(word)
        Positive_Score = len(pw)
        # Calucalte the polarity Score
        Polarity_Score = (Positive_Score - Negative_Score)/ ((Positive_Score + Negative_Score) + 0.000001)
        # Calucate the Subjectivity Score 
        Subjectivity_Score = (Positive_Score + Negative_Score)/ (len(re.findall(r'\w+',cleaned_text)) + 0.000001)##Total Words after cleaning
        # Calucate Avg sentence len
        Average_Sentence_Length = len(cleaned_words)/len(re.split(r'[.!?]', cleaned_text))## the number of words / the number of sentences
        # Calucate the complex words
        a=[]
        for word in cleaned_words:
            if count_syllables(word) > 2:
                a.append(word)    
        complex_words = len(a)
        #Calucate Percentage of Complex words
        Percentage_of_Complex_words = complex_words/len(cleaned_words) ##the number of complex words / the number of words
        # Calucalte Fog Index 
        Fog_Index = calculate_fog_index(cleaned_text)
        ## Calucate Average Number of Words Per Sentence
        Average_Number_of_Words_Per_Sentence =len(cleaned_words)/len(re.split(r'[.!?]', cleaned_text))### the total number of words / the total number of sentences
        ## Calucate Word Count
        word_count = len(cleaned_words)
        ## Count Syllable per word 
        b=0
        for words in cleaned_words:
            b +=count_syllables(words)  
        Syllable_Count_Per_Word = b
        ## Count personal_pronouns
        Personal_pronoun = count_personal_pronouns(cleaned_text)
        ## Calucate Average_Word_Length
        a = Average_Word_Length(cleaned_text)
        # creating the new columns for each score and stamping the data     
        index=df[df['URL_ID']==category].index[0]
        df.loc[index,'Positive_Score'] = Positive_Score
        df.loc[index,'Negative_Score'] = Negative_Score
        df.loc[index,'Polarity_Score'] = Polarity_Score
        df.loc[index,'Subjectivity_Score'] = Subjectivity_Score
        df.loc[index,'Average_Sentence_Length'] = Average_Sentence_Length
        df.loc[index,'complex_words'] = complex_words
        df.loc[index,'Percentage_of_Complex_words'] = Percentage_of_Complex_words
        df.loc[index,'Fog_Index'] = Fog_Index
        df.loc[index,' Average_Number_of_Words_Per_Sentence'] =  Average_Number_of_Words_Per_Sentence
        df.loc[index,'word_count'] = word_count
        df.loc[index,'Syllable_Count_Per_Word'] = Syllable_Count_Per_Word
        df.loc[index,'Personal_pronoun'] = Personal_pronoun
        df.loc[index,'Average_Word_Length'] = a

    df.to_excel('Output_data_structur.xlsx', index=False)

    
    
    




# In[12]:


### Step 8: Run the sentiment analys for the output file 


# In[13]:


stop_words_folder = r'C:\Users\cherukuri\Downloads\DS Assignemets\Stop words'
text_files_folder = r'C:\Users\cherukuri\Downloads\DS Assignemets\Extracted_Articles'
folder_path = r'C:\Users\cherukuri\Downloads\DS Assignemets\Dictionary'


# In[14]:


Sentiment_analysis(text_files_folder,stop_words_folder,folder_path)

