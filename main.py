import streamlit as st
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import os
from nltk.corpus import wordnet
nltk.download('wordnet')
nltk.download("punkt")
nltk.download("stopwords")

from transformers import pipeline

import logging, sys
logging.disable(sys.maxsize)

#import poe
#client = poe.Client("f4bW8Bq6vAgqUSJfQWmMZg%3D%3D")

import logging
import sys
import json

#token = sys.argv[1]
#poe.logger.setLevel(logging.INFO)

# Function to preprocess the text
def preprocess_text(text):
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
    return " ".join(filtered_words)

# Read sentences from CSV or plain text file
def read_sentences1(file_path):
    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)# Replace 'your_column_name' with the actual column name in your CSV file.
        sentences = df[df.columns.values[0]].tolist()  # Replace 'your_column_name'
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)# Replace 'your_column_name' with the actual column name in your CSV file.
        sentences = df[df.columns.values[0]].tolist()  # Replace 'your_column_name'

    else:
        with open(file_path, "r") as file:
            sentences = file.readlines()
    return sentences

def read_sentences(txt):
  sentences = input().split(',')
  return sentences

# Topic modeling using LDA
def topic_modeling(sentences, num_topics):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(sentences)
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(X)
    return lda, vectorizer

# Assign sentences to themes based on dominant topics
def assign_sentences_to_themes(lda, vectorizer, sentences):
    theme_sentences = {i: [] for i in range(lda.n_components)}
    for sent in sentences:
        X_sent = vectorizer.transform([sent])
        topic_idx = lda.transform(X_sent).argmax()
        theme_sentences[topic_idx].append(sent)
    return theme_sentences

# Visualize themes using a bar chart and pie chart
def visualize_themes(theme_freq):
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.bar(theme_freq.keys(), theme_freq.values())
    plt.xlabel("Themes")
    plt.ylabel("Frequency")
    plt.title("Themes Frequency (Bar Chart)")

    plt.subplot(1, 2, 2)
    plt.pie(theme_freq.values(), labels=theme_freq.keys(), autopct="%1.1f%%")
    plt.title("Themes Distribution (Pie Chart)")

    plt.tight_layout()
    #plt.savefig('plot.png')
    st.pyplot()

# Extract the most relevant words for each topic
def extract_topic_keywords(lda, vectorizer, num_words=5):
    feature_names = vectorizer.get_feature_names_out()
    topic_keywords = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[-num_words:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topic_keywords.append(top_words)
    return topic_keywords

def find_theme_of_word(word):


        # Get the synsets (word meanings) of the given word
        word_synsets = wordnet.synsets(word.lower())

        # If no synsets found for the word, return None
        if not word_synsets:
            return None

        # Find the most common theme (hypernym) of the word's synsets
        themes = {}
        for synset in word_synsets:
            hypernyms = synset.hypernyms()
            for hypernym in hypernyms:
                themes[hypernym] = themes.get(hypernym, 0) + 1

        # Sort the themes by their frequency in descending order
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)

        # Return the theme of the word (most frequent hypernym)
        theme_word = sorted_themes[0][0].lemmas()[0].name()
        return theme_word

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))    

if "model1_computed" not in st.session_state:
    st.session_state.model1_computed = False
if "model2_computed" not in st.session_state:
    st.session_state.model2_computed = False

st.title("THEME GENERATOR")
txt = st.text_area("Enter text here", value="")
sentences = txt.split(',')
final_text = list(sentences)

def main():
    
    num_topics = 5  # Number of themes to generate (you can adjust this)

    #sentences = read_sentences(txt)
    preprocessed_sentences = [preprocess_text(sent) for sent in sentences]

    lda, vectorizer = topic_modeling(preprocessed_sentences, num_topics)
    theme_sentences = assign_sentences_to_themes(lda, vectorizer, sentences)
    global theme_freq
    theme_freq = {f"Theme {i + 1}": len(theme_sentences[i]) for i in range(num_topics)}

    # Extract most relevant words for each topic
    topic_keywords = extract_topic_keywords(lda, vectorizer)

    # Print themes and their most relevant words
    global list_key
    list_key = []
    for theme, freq, keywords in zip(theme_freq.keys(), theme_freq.values(), topic_keywords):
        print(f"{theme}: {freq} sentences")
        print("Keywords:", ", ".join(keywords))
        list_key.append(keywords)

    #visualize_themes(theme_freq)
    #return list_key
    #print(list_key)
    global l_theme
    l_theme = []
    for i in list_key:
      print(i)
      common_theme = find_theme_of_word(i[0])
      print("Common Theme:", common_theme)
      l_theme.append(common_theme)

    for i in range(5):
        theme_freq[l_theme[i]] = theme_freq.pop(list(theme_freq)[0])
    print(theme_freq)
      
    return l_theme, theme_freq, list_key

#def func():
#    txt = list(split(sentences,5))
#
#   prompt1 = 'Find the domain/theme of '+str(txt[0])+' in one word'
#    prompt2 = 'Find the domain/theme of '+str(txt[1])+' in one word'
#    prompt3 = 'Find the domain/theme of '+str(txt[2])+' in one word'
#    prompt4 = 'Find the domain/theme of '+str(txt[3])+' in one word'
#    prompt5 = 'Find the domain/theme of '+str(txt[4])+' in one word'

#    global list_theme
#    list_theme = []

#    for i in client.send_message("acouchy",prompt1, with_chat_break=True):
#      text1 = i["text_new"]
#      list_theme.append(text1)
#
#    for i in client.send_message("acouchy",prompt2, with_chat_break=True):
#      text2 = i["text_new"]
#      list_theme.append(text2)

#    for i in client.send_message("acouchy",prompt3, with_chat_break=True):
#      text3 = i["text_new"]
#      list_theme.append(text3)

#    for i in client.send_message("acouchy",prompt4, with_chat_break=True):
#      text4 = i["text_new"]
#      list_theme.append(text4)

#    for i in client.send_message("acouchy",prompt5, with_chat_break=True):
#      text5 = i["text_new"]
#      list_theme.append(text5)

#    return list_theme

def main1():
    global list_key
    list_key = []
    sentiment_pipeline = pipeline("sentiment-analysis")
    list_txt = list(sentences)
    for i in range(5):
        list_key.append(sentiment_pipeline(list_txt[i]))  
    return list_key    

def plot1():
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = l_theme
    sizes = [27.1, 15.3, 18.6, 15.3, 23.7]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)
    
if __name__ == "__main__":
    #main()  
    
    #theme_f = {'act': 16, 'move': 9, 'ability': 11, 'work': 9, 'change': 14} 
    col1, col2 = st.columns(2)

        # Left column content
    with col1:
        if st.button("NLP Model") or st.session_state.model1_computed:
            main()
            #st.text_area(label='',value=l_theme, height=20)
            
            for i in l_theme:
                #st.button(str(i))
                out = []
                t = str(i)
                
                if st.button(t):
                    
                    for j in final_text:
                        for k in list_key[l_theme.index(t)]:
                            if k in j:
                                out.append(j)
                    st.write('Words under this theme...')            
                    st.write(list_key[l_theme.index(t)])            
                    st.write(str(len(out))+' sentences')
                    st.write(out)
                                
            if st.button("Pie Chart 1"):
                plot1()    
            
            st.session_state.model1_computed = True    
        # Right column content
    with col2:
        if st.button("Pos/Neg") or st.session_state.model2_computed:
            main1()
            for i in list_theme:
                st.write(str(i))     
                
            st.session_state.model2_computed = True    
