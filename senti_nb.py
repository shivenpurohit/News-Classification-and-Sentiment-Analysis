import csv
import sqlite3
import re
from nltk.tokenize import word_tokenize
from string import punctuation 
from nltk.corpus import stopwords
from nltk.corpus import sentiwordnet as swn
import numpy as np 
from sklearn.feature_extraction.text import CountVectorizer 

# build training data
def createTrainingCorpus():     
    trainingData=[]
    filename = '/home/pronks/Desktop/News_project/Sentiment/corpus.csv'
    try:
        for label in ["positive","negative"]:
            with open(filename, 'rb') as f:
                reader = csv.reader(f)
                c=1
                for row in reader:
                    if(str(row[1]) == label):
                            news={'text':row[0], 'label':row[1]} 
                            trainingData.append(news)
    except Exception, e: 
        print e
    return trainingData

print 
print
print "Building Training Data"
trainingData=createTrainingCorpus()
#print trainingData


# A class to preprocess all the newss, both test and training
class PreProcessnewss:
    def __init__(self):
        self._stopwords=set(stopwords.words('english')+list(punctuation)+['AT_USER','URL', '-', '--', '---', '----', '-----', '..', '...', '....', '.....', '......', '`', '``', '```', '````', '`````', '``````', "'", "''", 'br'])
        
    def processnewss(self,list_of_newss):
        processednewss=[]
        c=1
        for news in list_of_newss:
            processednewss.append((self._processnews(news["text"]),news["label"]))
        return processednewss
    
    def _processnews(self,news):
        news=re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',news)     
        news=re.sub('@[^\s]+','AT_USER',news)
        news=re.sub(r'#([^\s]+)',r'\1',news)
        news=word_tokenize(news)
        return [word.lower() for word in news if word not in self._stopwords]
    
newsProcessor=PreProcessnewss()
ppTrainingData=newsProcessor.processnewss(trainingData)
#print ppTrainingData[:5]


# Extract features and train your classifier
# We'll use - Naive Bayes 
import nltk 

def buildVocabulary(ppTrainingData):
    all_words=[]
    for (words,sentiment) in ppTrainingData:
        all_words.extend(words)
    wordlist=nltk.FreqDist(all_words)
    word_features=wordlist.keys()
    return word_features

# NLTK has an apply_features function that takes in a user-defined function to extract features from training data. We want to define our 
# extract features function to take each news in the training data and represent it with the presence or absence of a word in the vocabulary 

def extract_features(news):
    news_words=set(news)
    features={}
    for word in word_features:
        features['contains(%s)' % word]=(word in news_words)
    return features 

# Now we can extract the features and train the classifier 
word_features = buildVocabulary(ppTrainingData)
trainingFeatures=nltk.classify.apply_features(extract_features,ppTrainingData)
# apply_features will take the extract_features function we defined above, and apply it it each element of ppTrainingData.



NBayesClassifier=nltk.NaiveBayesClassifier.train(trainingFeatures)
# We now have a classifier that has been trained using Naive Bayes


# Test Data from database
# connect to the database
while (True):
    print
    choice=raw_input('Do you want to find sentiment news articles? (Y/N)  ')
    if(choice=='Y'):
        testData=[]
        try:
            ids=raw_input('Select the S.No. of article you want to find the sentiment...  ')
            conn = sqlite3.connect('/home/pronks/Desktop/News_project/database.sqlite')
            cur = conn.cursor()

            cur.execute('''SELECT story FROM NewsData WHERE id=?''', (ids,))
            row = cur.fetchone()
            text = row[0]
            testData.append({'label':None, 'text':str(text)})
        except Exception, e:
            print 'Error'
            print e
        ppTestData=newsProcessor.processnewss(testData)
        #print ppTestData


        # Run the classifier on test data 
        NBResultLabels=[NBayesClassifier.classify(extract_features(news[0])) for news in ppTestData]

        if NBResultLabels.count('positive')>NBResultLabels.count('negative'):
            #print "NB Result Positive Sentiment" 
            cur.execute('''UPDATE NewsData SET Sentiment=(?) WHERE id=?''', ('Positive', ids))
        else: 
            #print "NB Result Negative Sentiment" 
            cur.execute('''UPDATE NewsData SET Sentiment=(?) WHERE id=?''', ('Negative', ids))
        print NBResultLabels.count('positive'), NBResultLabels.count('negative')
        conn.commit()
    else:
        print 'Application stopped by User'
        break

