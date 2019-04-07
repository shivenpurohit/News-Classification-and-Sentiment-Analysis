import csv
import sqlite3
import re
from nltk.tokenize import word_tokenize
from string import punctuation 
from nltk.corpus import stopwords
from nltk.corpus import sentiwordnet as swn
import numpy as np 
from sklearn.feature_extraction.text import CountVectorizer 


def createTrainingCorpus():     
    trainingData=[]
    filename = 'corpus.csv'
    try:
        for label in ["positive","negative"]:
            with open(filename, 'rb') as f:
                reader = csv.reader(f)
                c=1
                for row in reader:
                    if(str(row[1]) == label):
                            tweet={'text':row[0], 'label':row[1]}
                            #tweet is a dictionary which already has tweet_id and label (positive/negative/neutral)
                            # Add another attribute now, the tweet text 
                            trainingData.append(tweet)
    except Exception, e: 
        print e
    return trainingData

print "Building Training Data"
trainingData=createTrainingCorpus()
#print trainingData


# 2b. A class to preprocess all the tweets, both test and training
# We will use regular expressions and NLTK for preprocessing  

class PreProcessTweets:
    def __init__(self):
        self._stopwords=set(stopwords.words('english')+list(punctuation)+['AT_USER','URL', '-', '--', '---', '----', '-----', '..', '...', '....', '.....', '......', '`', '``', '```', '````', '`````', '``````', "'", "''", 'br'])
        
    def processTweets(self,list_of_tweets):
        # The list of tweets is a list of dictionaries which should have the keys, "text" and "label"
        processedTweets=[]
        # This list will be a list of tuples. Each tuple is a tweet which is a list of words and its label
        c=1
        for tweet in list_of_tweets:
            processedTweets.append((self._processTweet(tweet["text"]),tweet["label"]))
        return processedTweets
    
    def _processTweet(self,tweet):
        # 2. Replace links with the word URL 
        tweet=re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)     
        # 3. Replace @username with "AT_USER"
        tweet=re.sub('@[^\s]+','AT_USER',tweet)
        # 4. Replace #word with word 
        tweet=re.sub(r'#([^\s]+)',r'\1',tweet)
        tweet=word_tokenize(tweet)
        # This tokenizes the tweet into a list of words 
        # Let's now return this list minus any stopwords with lower case
        return [word.lower() for word in tweet if word not in self._stopwords]
    
tweetProcessor=PreProcessTweets()
ppTrainingData=tweetProcessor.processTweets(trainingData)
#print ppTrainingData[:5]


# 2c. Extract features and train your classifier
# Support Vector Machines 

# We have to change the form of the data slightly. SKLearn has a CountVectorizer object. 
# It will take in documents and directly return a term-document matrix with the frequencies of 
# a word in the document. It builds the vocabulary by itself. We will give the trainingData 
# and the labels separately to the SVM classifier and not as tuples. 
# Another thing to take care of, if you built the Naive Bayes for more than 2 classes, 
# SVM can only classify into 2 classes - it is a binary classifier. 

svmTrainingData=[' '.join(tweet[0]) for tweet in ppTrainingData]
# Creates sentences out of the lists of words 

vectorizer=CountVectorizer(min_df=1)
X=vectorizer.fit_transform(svmTrainingData).toarray()
# We now have a term document matrix 
vocabulary=vectorizer.get_feature_names()

# Now for the twist we are adding to SVM. We'll use sentiwordnet to add some weights to these 
# features 

swn_weights=[]

for word in vocabulary:
    try:
        # Put this code in a try block as all the words may not be there in sentiwordnet (esp. Proper
        # nouns). Look for the synsets of that word in sentiwordnet 
        synset=list(swn.senti_synsets(word))
        # use the first synset only to compute the score, as this represents the most common 
        # usage of that word 
        common_meaning =synset[0]
        # If the pos_Score is greater, use that as the weight, if neg_score is greater, use -neg_score
        # as the weight 
        if common_meaning.pos_score()>common_meaning.neg_score():
            #print word, 'pos'
            weight=common_meaning.pos_score()
        elif common_meaning.pos_score()<common_meaning.neg_score():
            #print word, 'neg'
            weight=-1*common_meaning.neg_score()
        else: 
            #print 'neu'
            weight=0
    except: 
        weight=0
    swn_weights.append(weight)


# Let's now multiply each array in our original matrix with these weights 
# Initialize a list

swn_X=[]
for row in X: 
    swn_X.append(np.multiply(row,np.array(swn_weights)))
# Convert the list to a numpy array 
swn_X=np.vstack(swn_X)

# We have our documents ready. Let's get the labels ready too. 
# Lets map positive to 1 and negative to 2 so that everything is nicely represented as arrays 
labels_to_array={"positive":1,"negative":2}
labels=[labels_to_array[tweet[1]] for tweet in ppTrainingData]
y=np.array(labels)

# Let's now build our SVM classifier 
from sklearn.svm import SVC 
SVMClassifier=SVC()
SVMClassifier.fit(swn_X,y)


# Test Data from database
# connect to the database
while (True):
    choice=raw_input('Do you want to classify news articles? (Y/N)  ')
    if(choice=='Y'):
        testData=[]
        try:
            ids=raw_input('Select the S.No. of article you want to classify...  ')
            conn = sqlite3.connect('/home/pronks/Desktop/News_project/database.sqlite')
            cur = conn.cursor()

            cur.execute('''SELECT story FROM NewsData WHERE id=?''', (ids))
            row = cur.fetchone()
            text = row[0]
            testData.append({'label':None, 'text':str(text)})
        except Exception, e:
            print 'Error'
            print e
        ppTestData=tweetProcessor.processTweets(testData)
        #print ppTestData

    # Step 2d: Run the classifier on the 100 downloaded tweets 

        # Now SVM 
        SVMResultLabels=[]
        for tweet in ppTestData:
            tweet_sentence=' '.join(tweet[0])
            svmFeatures=np.multiply(vectorizer.transform([tweet_sentence]).toarray(),np.array(swn_weights))
            SVMResultLabels.append(SVMClassifier.predict(svmFeatures)[0])
        print SVMResultLabels
            # predict() returns  a list of numpy arrays, get the first element of the first array 
            # there is only 1 element and array

        # Step 3 : GEt the majority vote and print the sentiment 
            
        if SVMResultLabels.count(1)>SVMResultLabels.count(2):
            print SVMResultLabels.count(1), SVMResultLabels.count(2)
            print "SVM Result Positive Sentiment" + str(100*SVMResultLabels.count(1)/len(SVMResultLabels))+"%"
        else: 
            print SVMResultLabels.count(1), SVMResultLabels.count(2)
            print "SVM Result Negative Sentiment" + str(100*SVMResultLabels.count(2)/len(SVMResultLabels))+"%"

        testData[0:]
        SVMResultLabels[0:]

        #Looks like most of these tweets are actually neutral , And our SVM is classifying them as -ve,
        # But it classified the positive tweet correctly. 

        # A few next steps possible here 
        # Remove all neutral words according to sentiwordnet from the vocabulary. 
        # Look at things like ALL CAPS , emoticons etc 

        # GEt a corpus with more varied tweets (This one has only tech related tweets, so it works for our 
        # search term (Apple) but might not for others. )

    else:
        print 'Application stopped by User'
        break

