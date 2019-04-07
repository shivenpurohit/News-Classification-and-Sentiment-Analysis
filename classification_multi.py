import requests
import urllib2
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
from math import log
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import codecs
import sqlite3
import csv


def fetchTrainingData(label):
    urlBodies = {}
    filename = '/home/pronks/Desktop/News_project/classification/news_class_corpus.csv'
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        c=0
        for row in reader:
            c=c+1
            if(str(row[2]) == label):
                #print c
                urlBodies[row[0].encode("utf-8", 'ignore')] = row[1].encode("utf-8", 'ignore')
    return urlBodies


# In[5]:

# Now for the frequency summarizer class - which we have encountered
# before. To quickly jog our memories - given an (title,article-body) tuple
# the frequency summarizer has easy ways to find the most 'important'
# sentences, and the most important words.
# Important = most frequent, excluding 'stopwords' which are generic
# words like 'the' etc which can be ignored
class FrequencySummarizer:
    def __init__(self,min_cut=0.1,max_cut=0.9):
        # class constructor - takes in min and max cutoffs for 
        # frequency
        self._min_cut = min_cut
        self._max_cut = max_cut
        self._stopwords = set(stopwords.words('english') +
                              list(punctuation) +
                              [u"'s",'"'])
        # notice how the stopwords are a set, not a list. 
        # its easy to go from set to list and vice-versa
        # (simply use the set() and list() functions) - 
        # but conceptually sets are different from lists
        # because sets don't have an order to their elements
        # while lists do
    
    def _compute_frequencies(self,word_sent,customStopWords=None):
        freq = defaultdict(int)
        # we have encountered defaultdict objects before
        if customStopWords is None:
            stopwords = set(self._stopwords)
        else:
            stopwords = set(customStopWords).union(self._stopwords)
        for sentence in word_sent:
            for word in sentence:
                if word not in stopwords:
                    freq[word] += 1
        m = float(max(freq.values()))
        for word in freq.keys():
            freq[word] = freq[word]/m
            if freq[word] >= self._max_cut or freq[word] <= self._min_cut:
                del freq[word]
        return freq
    
    def extractFeatures(self,article,n,customStopWords=None):
        # The article is passed in as a tuple (text, title)
        #print article
        text = article
        # extract the text
        #title = article[1]
        # extract the title
        sentences = sent_tokenize(text)
        # split the text into sentences
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        #print word_sent
        # split the sentences into words

        self._freq = self._compute_frequencies(word_sent,customStopWords)
        # calculate the word frequencies using the member function above
        if n < 0:
            # how many features (words) to return? IF the user has
            # asked for a negative number, this is a sign that we don't
            # do any feature selection - we return ALL features
            # THis is feature extraction without any pruning, ie no
            # feature selection (beyond simply picking words as the features)
            return nlargest(len(self._freq_keys()),self._freq,key=self._freq.get)
        else:
            # if the calling function has asked for a subset then
            # return only the 'n' largest features - ie here the most
            # important words (important == frequent, barring stopwords)
            return nlargest(n,self._freq,key=self._freq.get)
        # let's summarize what we did here. 
    
    def extractRawFrequencies(self, article):
        # very similar, except that this method will return the 'raw'
        # frequencies - literally just the word counts
        text = article
        #title = article[1]
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        freq = defaultdict(int)
        for s in word_sent:
            for word in s:
                if word not in self._stopwords:
                    freq[word] += 1
        return freq
    
    def summarize(self, article,n):
        text = article
        #title = article[1]
        sentences = sent_tokenize(text)
        word_sent = [word_tokenize(s.lower()) for s in sentences]
        self._freq = self._compute_frequencies(word_sent)
        ranking = defaultdict(int)
        for i,sentence in enumerate(word_sent):
            for word in sentence:
                if word in self._freq:
                    ranking[i] += self._freq[word]
        sentences_index = nlargest(n,ranking,key=ranking.get)

        return [sentences[j] for j in sentences_index]


# Biuld training data
print 
print 
print 'Building training data'
theHinduNationalArticles = fetchTrainingData('national')
theHinduInternationalArticles = fetchTrainingData('international')
theHinduBusinessArticles = fetchTrainingData('business')
theHinduSportsArticles = fetchTrainingData('sports')
theHinduOtherArticles = fetchTrainingData('other')

articleSummaries = {}
for sportsUrlDictionary in theHinduSportsArticles:
    if theHinduSportsArticles[sportsUrlDictionary][0] is not None:
        if len(theHinduSportsArticles[sportsUrlDictionary][0]) > 0:
            fs = FrequencySummarizer()
            #print theHinduSportsArticles[sportUrlDictionary]
            summary = fs.extractFeatures(theHinduSportsArticles[sportsUrlDictionary],25)
            articleSummaries[sportsUrlDictionary] = {'feature-vector': summary,'label': 'sports'}

for businessUrlDictionary in theHinduBusinessArticles:
    if theHinduBusinessArticles[businessUrlDictionary][0] is not None:
        if len(theHinduBusinessArticles[businessUrlDictionary][0]) > 0:
            fs = FrequencySummarizer()
            #print theHinduSportsArticles[sportUrlDictionary]
            summary = fs.extractFeatures(theHinduBusinessArticles[businessUrlDictionary],25)
            articleSummaries[sportsUrlDictionary] = {'feature-vector': summary,'label': 'business'}

for nationalUrlDictionary in theHinduNationalArticles:
    if theHinduNationalArticles[nationalUrlDictionary][0] is not None:
        if len(theHinduNationalArticles[nationalUrlDictionary][0]) > 0:
            fs = FrequencySummarizer()
            #print theHinduSportsArticles[sportUrlDictionary]
            summary = fs.extractFeatures(theHinduNationalArticles[nationalUrlDictionary],25)
            articleSummaries[nationalUrlDictionary] = {'feature-vector': summary,
                                           'label': 'national'}

for internationalUrlDictionary in theHinduInternationalArticles:
    if theHinduInternationalArticles[internationalUrlDictionary][0] is not None:
        if len(theHinduInternationalArticles[internationalUrlDictionary][0]) > 0:
            fs = FrequencySummarizer()
            #print theHinduSportsArticles[sportUrlDictionary]
            summary = fs.extractFeatures(theHinduInternationalArticles[internationalUrlDictionary],25)
            articleSummaries[internationalUrlDictionary] = {'feature-vector': summary,
                                           'label': 'international'}

for otherUrlDictionary in theHinduOtherArticles:
    if theHinduOtherArticles[otherUrlDictionary][0] is not None:
        if len(theHinduOtherArticles[otherUrlDictionary][0]) > 0:
            fs = FrequencySummarizer()
            #print theHinduSportsArticles[sportUrlDictionary]
            summary = fs.extractFeatures(theHinduOtherArticles[otherUrlDictionary],25)
            articleSummaries[otherUrlDictionary] = {'feature-vector': summary,
                                           'label': 'other'}


#naive-bayes classifier training
# cummulative raw frequency 
cumulativeRawFrequencies = {'national':defaultdict(int),'business':defaultdict(int),'international':defaultdict(int),'other':defaultdict(int),'sports':defaultdict(int)}
trainingData = {'sports':theHinduSportsArticles, 'business':theHinduBusinessArticles, 'international':theHinduInternationalArticles, 'national':theHinduNationalArticles, 'other':theHinduOtherArticles}
for label in trainingData:
    for articleUrl in trainingData[label]:
        if len(trainingData[label][articleUrl][0]) > 0:
            fs = FrequencySummarizer()
            # rawFrequencies is the frequency of a word in the article in a dictionry {'word':freq}
            rawFrequencies = fs.extractRawFrequencies(trainingData[label][articleUrl])
            for word in rawFrequencies:
                # cummulativeRawFrequencies is the total frequency of a word in all the arrticles of a particluar label in training data
                cumulativeRawFrequencies[label][word] += rawFrequencies[word]


# connect to the database
while (True):
    print
    choice=raw_input('Do you want to classify news articles? (Y/N)  ')
    if(choice=='Y'):
        try:
            ids=raw_input('Select the S.No. of article you want to classify...  ')
            conn = sqlite3.connect('/home/pronks/Desktop/News_project/database.sqlite')
            cur = conn.cursor()

            cur.execute('''SELECT story FROM NewsData WHERE id=?''', (ids,))
            row = cur.fetchone()
            text = str(row[0])

        except Exception, e:
            print 'Error'
            print e


        #feature-vector test data
        fs = FrequencySummarizer()
        testArticleSummary = fs.extractFeatures(text, 25)
        #print testArticleSummary
        if(len(testArticleSummary)>0):
            # P(label) -- prior probability -- probabaility of a article to be sports, national etc. article
            # This is taken as 0.2 for all as the number of articles of all the labels are equal
            sportiness = 0.2
            businessiness = 0.2
            otherness=0.2
            internationalness=0.2
            nationalness=0.2

            # for each 'feature' of the test instance - 
            for word in testArticleSummary:
                if word in cumulativeRawFrequencies['sports']:
                    # we multiply the sportiness by the probability of this word appearing in a sports article (based on the training data)
                    # cumulativeRawFrequencies['sports'][word]/float(sum(cumulativeRawFrequencies['sports'].values())) is P(word/label) -- 
                    # probablity of a word to appear in the whole corpus
                    # sportiness is now P(word/label)*P(label)
                    sportiness *= 1e3*cumulativeRawFrequencies['sports'][word] / float(sum(cumulativeRawFrequencies['sports'].values()))
                else:
                    # If the word does not appear in the sports articles of the training data at all,we could simply
                    # set that probability to zero - in fact doing so is the 'correct'way mathematically, because that way all of the probabilities 
                    # wouldsum to 1. But that would lead to 'snap' decisions since the sportsiness would instantaneously become 0. To prevent this, we 
                    # decide to take the probability as some very small number (here 1 in 1000, which is actually not all that low)
                    sportiness /= 1e3
                if word in cumulativeRawFrequencies['business']:
                    businessiness *= 1e3*cumulativeRawFrequencies['business'][word] / float(sum(cumulativeRawFrequencies['business'].values()))
                else:
                    businessiness /= 1e3
                if word in cumulativeRawFrequencies['national']:
                    nationalness *= 1e3*cumulativeRawFrequencies['national'][word] / float(sum(cumulativeRawFrequencies['national'].values()))
                else:
                    nationalness /= 1e3
                if word in cumulativeRawFrequencies['other']:
                    otherness *= 1e3*cumulativeRawFrequencies['other'][word] / float(sum(cumulativeRawFrequencies['other'].values()))
                else:
                    otherness /= 1e3
                if word in cumulativeRawFrequencies['international']:
                    internationalness *= 1e3*cumulativeRawFrequencies['international'][word] / float(sum(cumulativeRawFrequencies['international'].values()))
                else:
                    internationalness /= 1e3


            # we are almost done! Now we simply need to scale the sportiness and non-sportiness by the probabilities of overall sportiness and
            # non-sportiness. THis is simply the number of words in the sport and non-sport articles respectively, as a proportion of the total 
            # number of words

            # total is P(W) -- probability of a word in corpus
            total=(float(sum(cumulativeRawFrequencies['sports'].values())) + float(sum(cumulativeRawFrequencies['business'].values())) + float(sum((cumulativeRawFrequencies['other'].values()))) + float(sum((cumulativeRawFrequencies['national'].values()))) + float(sum((cumulativeRawFrequencies['international'].values()))))
            # float(sum(cumulativeRawFrequencies['sports'].values())) is P(S)
            sportiness *= float(sum(cumulativeRawFrequencies['sports'].values())) / total
            businessiness *= float(sum(cumulativeRawFrequencies['business'].values())) / total
            nationalness *= float(sum(cumulativeRawFrequencies['national'].values())) / total
            internationalness *= float(sum(cumulativeRawFrequencies['international'].values())) / total
            otherness *= float(sum(cumulativeRawFrequencies['other'].values())) / total

            ans=max(nationalness, internationalness, sportiness, businessiness, otherness)
            if(ans==sportiness):
                cur.execute('''UPDATE NewsData SET Genre=(?) WHERE id=?''', ('Sports', ids))
            elif(ans==nationalness):
                cur.execute('''UPDATE NewsData SET Genre=(?) WHERE id=?''', ('National', ids))
            elif(ans==internationalness):
                cur.execute('''UPDATE NewsData SET Genre=(?) WHERE id=?''', ('International', ids))
            elif(ans==businessiness):
                cur.execute('''UPDATE NewsData SET Genre=(?) WHERE id=?''', ('Business and Economy', ids))
            elif(ans==otherness):
                cur.execute('''UPDATE NewsData SET Genre=(?) WHERE id=?''', ('Others', ids))
            conn.commit()
            print nationalness, internationalness, sportiness, businessiness, otherness
        else:
            print 'Inappropiate test vector'
    else:
        print 'Application stopped by user'
        break




