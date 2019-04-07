import sys
from bs4 import BeautifulSoup
import HTML
import urllib
import datetime
import os.path
import codecs
import sqlite3


def scrape(url, n):

    # current date
    try:
        date=datetime.datetime.now().strftime ("%Y-%m-%d")
    except Exception, e:
        print 'Error while fetching current date\n'+str(e)
    
    #output file initialize
    savedirDown='business-standard/'+str(date)
    savedirClean='business-standard/'+str(date)

    opfile='/home/pronks/Desktop/News_project/database'


    #databse initialization
    try:
        conn = sqlite3.connect(opfile+'.sqlite')
        cur = conn.cursor()

        cur.executescript('''
            DROP TABLE IF EXISTS NewsData;
            CREATE TABLE NewsData(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                Title TEXT,
                Author TEXT,
                Date_of_Publishing TEXT,
                Story TEXT,
                Summary TEXT,
                Genre TEXT,
                Sentiment TEXT
                );
            ''')
    except:
        print 'Error while initializing database'



    for i in range(0,int(n),1):
        title=None
        website=None
        author=None
        story=None
        
        if len(url[i])>1: 
            #
            #create html code file
            try:
                downfile=str(url[i]).split('/')
                downfile=downfile[len(downfile)-1]
                downfile=downfile.strip()
                downfile=savedirDown+'/'+downfile+'.html'
                if not os.path.isfile(downfile):
                    if not os.path.exists(savedirDown):
                        os.makedirs(savedirDown)
                    htm = urllib.urlopen(url[i])

                    # take whole html code into soup onject for html extraction
                    soup = BeautifulSoup(htm, 'html.parser')
                    df=open(downfile, 'a+')
                    df.write(soup.encode("utf-8", 'replace'))
                    df.close()
                else:
                    # take whole html code into soup onject for html extraction
                    htm=open(downfile,'r')
                    soup=BeautifulSoup(htm, 'html.parser')
            except Exception, e:
                print 'html error'
                print e
                continue

        
            # title
            try:
                for link in soup.find_all('meta'):
                    if(link.get('property')=='og:title'):
                        #print link.get('content')
                        title=(link.get('content')).encode("utf-8", 'replace')
            except:
                title=('Error while fetching title name\n'+str(err)).encode('utf-8', 'replace') 
            
            # website name
            try:
                website=url[i].encode("utf-8", 'replace')
            except Exception, err:
                website=('Error while fetching website name\n'+str(err)).encode('utf-8', 'replace')
            
            
            # author name   
            try:
                for link in soup.find_all('meta'):
                    if(link.get('name')=='author'):
                        #print link.get('content')
                        author=(link.get('content')).encode("utf-8", 'replace')
            except Exception, e:
                author=('Error while fetching author name\n'+str(e)).encode('utf-8', 'replace')


            # date of publishing
            try:
                datepublish=soup.find("meta", {"itemprop" : "datePublished"})
                datepublish=(datepublish.get('content')).encode("utf-8", 'replace')
                datepublish=datepublish.split("T")
                datepublish=datepublish[0]
                #print datepublish
            except:
                datepublish=date;

            
            #story
            try:
                results = soup.findAll("span", {"itemscope" : "articleBody"})
                story=(results[0].text).encode("utf-8", 'replace')
                story=story.strip()
                story=story.replace('\n\n', ' ')
                story=story.replace('\n', ' ')
                story=story.replace('  ', '')
                if story and len(story) > 0:
                    #print story
                    out_txt = []
                    for row in story:
                        out_txt.append([
                            "".join(a if ord(a) < 128 else ' ' for a in t)
                            for t in row
                        ])
                    story=''
                    story=story.join(str(r) for v in out_txt for r in v)
                #print story
            
            except Exception, err:
                story=('Error while fetching story\n'+str(err)).encode('utf-8', 'replace')
            #print story
            
            #insert into html table/database
            try:
                #t.rows.append([title, author, website, datepublish, story])
                cur.execute('''INSERT OR IGNORE INTO NewsData (Title, Author, Date_of_Publishing, Story) VALUES ( ?, ?, ?, ? )''', 
                    (buffer(title), buffer(author), buffer(datepublish), buffer(story)))
                conn.commit()
            except Exception,e:
                print 'Error while inserting into html table/database',e
            #print t


            
def Main():
    try:
        #variables initialize
        url=None
        n=None

        #input file
        rf=open("/home/pronks/Desktop/News_project/crawler/business-standard/bs.txt", 'r')
        url=rf.readlines()
        print'Total number of news stories available are: ', len(url)
        n=raw_input('How many do you want to scrape?  ')
        #print url
        rf.close()

        # call scrape function
        scrape(url, n)
    except Exception, e:
        print e

if __name__ == '__main__':
    Main()

