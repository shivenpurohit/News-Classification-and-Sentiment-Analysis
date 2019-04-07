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


hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


def scrapeTheHinduLinks(url):
	urls=[]
	req=urllib2.Request(url, headers=hdr)
	htm=urllib2.urlopen(req)
	soup=BeautifulSoup(htm, 'html.parser')

	r=soup.find_all('ul', {"class":"archive-list"})
	r=r[0].find_all('li')
	for links in r:
		link=links.a.get('href')
		urls.append(link)
	return urls

def scrapeTheHinduArticles(url):
	urlBodies = {}
	for i in range(0, 10, 1):
		story=None
		#print url[i]
		htm = urllib2.urlopen(url[i])
		soup = BeautifulSoup(htm, 'html.parser')

		#story
		try:
			results = soup.find_all("p")
			for p in results:
				if(story is None):
					story=p.text.strip()
				else:
					y=''
					y=(p.text).strip()
					story=story+y    
					story=story.replace('\n', ' ')
					story=story.replace('  ', '')
			if story and len(story) > 0:
				#print story
				urlBodies[url[i]] = story

		except Exception, e:
			story=('Error while fetching story\n'+str(e)).encode('utf-8', 'replace')
	return urlBodies


# In[5]:

# Now for the frequency summarizer class - which we have encountered
# before. To quickly jog our memories - given an (title,article-body) tuple
# the frequency summarizer has easy ways to find the most 'important'
# sentences, and the most important words. How is 'important' defined?
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



urlHinduSports = "http://www.thehindu.com/todays-paper/tp-sports/"
urlHinduNonSports = "http://www.thehindu.com/todays-paper/tp-business/"

url = scrapeTheHinduLinks(urlHinduSports)
theHinduSportsArticles = scrapeTheHinduArticles(url)
print theHinduSportsArticles

url = scrapeTheHinduLinks(urlHinduNonSports)
theHinduNonSportsArticles = scrapeTheHinduArticles(url)

articleSummaries = {}
for sportsUrlDictionary in theHinduSportsArticles:
    if theHinduSportsArticles[sportsUrlDictionary][0] is not None:
        if len(theHinduSportsArticles[sportsUrlDictionary][0]) > 0:
            fs = FrequencySummarizer()
            #print theHinduSportsArticles[sportUrlDictionary]
            summary = fs.extractFeatures(theHinduSportsArticles[sportsUrlDictionary],25)
            articleSummaries[sportsUrlDictionary] = {'feature-vector': summary,
                                           'label': 'Sports'}
for nonsportsUrlDictionary in theHinduNonSportsArticles:
    if theHinduNonSportsArticles[nonsportsUrlDictionary][0] is not None:
        if len(theHinduNonSportsArticles[nonsportsUrlDictionary][0]) > 0:
            fs = FrequencySummarizer()
            #print theHinduSportsArticles[sportUrlDictionary]
            summary = fs.extractFeatures(theHinduNonSportsArticles[nonsportsUrlDictionary],25)
            articleSummaries[nonsportsUrlDictionary] = {'feature-vector': summary,
                                           'label': 'Non-Sports'}


#naive-bayes
cumulativeRawFrequencies = {'Sports':defaultdict(int),'Non-Sports':defaultdict(int)}
trainingData = {'Sports':theHinduSportsArticles,'Non-Sports':theHinduNonSportsArticles}
for label in trainingData:
    for articleUrl in trainingData[label]:
        if len(trainingData[label][articleUrl][0]) > 0:
            fs = FrequencySummarizer()
            rawFrequencies = fs.extractRawFrequencies(trainingData[label][articleUrl])
            for word in rawFrequencies:
                cumulativeRawFrequencies[label][word] += rawFrequencies[word]


# connect to the database
try:
	conn = sqlite3.connect('/home/pronks/Desktop/News_project/scraper/business-standard/2017-03-02/bs_op_1.sqlite')
	cur = conn.cursor()

	cur.execute('SELECT story FROM NewsData WHERE id=1')
	row = cur.fetchone()
	text = row[0]

except Exception, e:
    print 'Error'
    print e


#feature-vector test data
fs = FrequencySummarizer()
testArticleSummary = fs.extractFeatures(text, 25)
#print testArticleSummary

sportiness = 1.0
nonsportiness = 1.0

# for each 'feature' of the test instance - 
for word in testArticleSummary:
    if word in cumulativeRawFrequencies['Sports']:
        # we multiply the sportiness by the probability of this word appearing in a sports article (based on the training data)
        sportiness *= 1e3*cumulativeRawFrequencies['Sports'][word] / float(sum(cumulativeRawFrequencies['Sports'].values()))
    else:
        # THis is worth paying attention to. If the word does not appear in the sports articles of the training data at all,we could simply
        # set that probability to zero - in fact doing so is the 'correct'way mathematically, because that way all of the probabilities 
        # wouldsum to 1. But that would lead to 'snap' decisions since the sportsiness would instantaneously become 0. To prevent this, we 
        # decide to take the probability as some very small number (here 1 in 1000, which is actually not all that low)
        sportiness /= 1e3
    if word in cumulativeRawFrequencies['Non-Sports']:
        # we multiply the sportsiness by the probability of this word appearing in a sports article (based on the training data)
        nonsportiness *= 1e3*cumulativeRawFrequencies['Non-Sports'][word] / float(sum(cumulativeRawFrequencies['Non-Sports'].values()))
    else:
        nonsportiness /= 1e3


# we are almost done! Now we simply need to scale the sportiness 
# and non-sportiness by the probabilities of overall sportiness and
# non-sportiness. THis is simply the number of words in the sport and 
# non-sport articles respectively, as a proportion of the total number
# of words

sportiness *= float(sum(cumulativeRawFrequencies['Sports'].values())) / (float(sum(cumulativeRawFrequencies['Sports'].values())) + float(sum(cumulativeRawFrequencies['Non-Sports'].values())))
nonsportiness *= float(sum(cumulativeRawFrequencies['Non-Sports'].values())) / (float(sum(cumulativeRawFrequencies['Sports'].values())) + float(sum(cumulativeRawFrequencies['Non-Sports'].values())))
if sportiness > nonsportiness:
    label = 'Sports'
else:
    label = 'Non-Sports'
print label, sportiness, nonsportiness


#print cumulativeRawFrequencies
