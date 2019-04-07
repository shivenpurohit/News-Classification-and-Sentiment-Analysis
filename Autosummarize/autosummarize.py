    
######################################################################################
# nltk - "natural language toolkit" is a python library with support for 
#         natural language processing. Super-handy.
# Specifically, we will use 2 functions from nltk
#  sent_tokenize: given a group of text, tokenize (split) it into sentences
#  word_tokenize: given a group of text, tokenize (split) it into words
#  stopwords.words('english') to find and ignored very common words ('I', 'the',...) 
#  to use stopwords, we need to run nltk.download() first - one-off setup
######################################################################################
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import sqlite3
import sys
import os

# setting utf-8 as default encoding
reload(sys)
sys.setdefaultencoding('utf-8')


######################################################################################
# Our first class, named FrequencySummarizer 
######################################################################################
class FrequencySummarizer:


    # The constructor named __init__. This will initialize the variables
    def __init__(self, min_cut=0.1, max_cut=0.9):
        # Words that have a frequency term lower than min_cut or higer than max_cut will be ignored. This is for some stopwords like words.
        self._min_cut = min_cut
        self._max_cut = max_cut 
        self._stopwords = set(stopwords.words('english') + list(punctuation))


    # next method takes in self (the special keyword for this same object) as well as a list of sentences, and outputs a dictionary, 
    # where the keys are words, and values are the frequencies of those words in the set of sentences
    def _compute_frequencies(self, word_sent):
        try:
            # in defaultdict, if the search key is not there it creates it instead of throwing exception
            freq = defaultdict(int)  

            # compute word frequency
            for s in word_sent:
              for word in s:
                if word not in self._stopwords:
                    freq[word] += 1
           
            
            # get the highest frequency of any word in the list of words
            m = float(max(freq.values()))
            
            for w in list(freq.keys()):
                # divide each frequency by that max value, so it is now between 0 and 1, this makes it easy to compare
                freq[w] = freq[w]/m
                
                #   filter out frequencies that are too high or too low. A trick that yields better results.
                if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
                    del freq[w]

            return freq
        except Exception as e:
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


    
    # next method (member function) which takes in self (the special keyword for this same object)
    # as well as the raw text, and the number of sentences we wish the summary to contain. Return the 
    # summary
    def summarize(self, text, n):
       
        try:
            # split the text into sentences
            sents = sent_tokenize(text)
            
            # assert is a way of making sure a condition holds true, else an exception is thrown
            # making sure the summary is shorter than the original article
            try:
                assert n <= len(sents)
            except:
                return list(text)

            # It converts each sentence to lower-case, then  splits each sentence into words, then takes all of those lists (1 per sentence)
            # and converts them into 1 big list
            word_sent = [word_tokenize(s.lower()) for s in sents]

            # compute sentence frequency
            self._freq = self._compute_frequencies(word_sent)

            # defaultdict to store sentences and their frequencies
            ranking = defaultdict(int)
           
            for i,sent in enumerate(word_sent):
                for w in sent:
                    # for each word in this sentence
                    if w in self._freq:
                        # if this is not a stopword (common word), add the frequency of that word  to the weightage assigned to that sentence 
                        ranking[i] += self._freq[w]
            
            # return the first n sentences with highest ranking, using the nlargest function
            sents_idx = nlargest(n, ranking, key=ranking.get)
            return [sents[j] for j in sents_idx]
        
        except Exception as e:
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)




#####################################################################################
# Main part
#####################################################################################

# connect to the database
while(True):
    print 
    choice=raw_input('Do you want to summarize news articles? (Y/N)  ')
    if(choice=='Y'):
        try:
            ids=raw_input('Select the S.No. of article you want to summarize...  ')
            conn = sqlite3.connect('/home/pronks/Desktop/News_project/database.sqlite')
            cur = conn.cursor()

            cur.execute('SELECT story FROM NewsData WHERE id=?', (ids))
            row = cur.fetchone()
            text = row[0]
        except Exception, e:
            print 'Error'
            print e

        # the article we would like to summarize
        try:
            n=raw_input('Enter the length of summarized story (in sentences)\n')
            fs = FrequencySummarizer()
            text=str(text).decode('utf-8', 'replace')


            # get a summary of this article that is n sentences long
            summary = fs.summarize(text, int(n))
            if len(summary)>1:
                summary = ''.join(summary)
            else:
                summary=summary[0]
            cur.execute('''UPDATE NewsData SET summary=(?) WHERE id=?''', (buffer(summary), ids))
            conn.commit()
        except Exception, e:
            print e
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
    else:
        print 'Application stopped by the user'
        break

