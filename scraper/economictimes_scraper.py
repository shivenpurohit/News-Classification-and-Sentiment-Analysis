import sys
from bs4 import BeautifulSoup
import HTML
import urllib
import datetime
import os.path
import codecs
import urllib2


def scrape(url):

    #flag initiation
    flag=None

    # find current date
    try:
        date=datetime.datetime.now().strftime ("%d-%m-%Y")
    except Exception, err:
        print 'Error while fetching current date\n'+str(err)

    #output file initialize
    savedirDown='Z:/end to end crawler/HtmlSource/economictimes'
    savedirClean='Z:/end to end crawler/CleanText/economictimes'

    if not os.path.exists(savedirClean):
        os.makedirs(savedirClean)
        if not os.path.isfile(savedirClean+'/flag.txt'):
            ff=open(savedirClean+'/flag.txt', 'w+')
            flag=1
            ff.write(str(flag))
            ff.close()
    else:
        ff=open(savedirClean+'/flag.txt', 'r+')
        flag=ff.readline()
        print flag
        flag=int(flag)+1
        ff.close()
        ff=open(savedirClean+'/flag.txt', 'w+')
        ff.write(str(flag))
        ff.close()
    opfile=savedirClean+'/et_op'+'_'+str(flag)+'.txt'


    for i in range(0,len(url),1):

        #html table initialize
        try:
            t = HTML.Table(header_row=['Title', 'Author', 'Website', 'Story'])
        except:
            print 'Error while initializing html table'
        #print t
        
        if len(url[i])>1:
            title=None
            website=None
            author=None
            story=None
            print (i+1)
            #print url[i]

            #download html file
            hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Connection': 'keep-alive'}
            try:
                downfile=str(url[i]).split('/')
                downfile=downfile[len(downfile)-3]
                downfile=downfile.strip()
                downfile=savedirDown+'/'+downfile+'.html'
                if not os.path.isfile(downfile):
                    if not os.path.exists(savedirDown):
                        os.makedirs(savedirDown)
                    req=urllib2.Request(url[i], headers=hdr)
                    htm=urllib2.urlopen(req)
                    soup = BeautifulSoup(htm, 'html.parser')
                    df=open(downfile, 'a+')
                    df.write(soup.encode("utf-8", 'replace'))
                    df.close()
                else:
                    print 'skip'
            except Exception, err:
                print 'html error'
                print err
                continue
            
            
            #title
            try:
                results=soup.findAll('title')
                title=(results[0].text).encode("utf-8", 'replace')
            except Exception, err:
                title = ('Error while fetching title\n'+str(err)).encode('utf-8', 'replace')


            # website name
            try:
                website=url[i].encode("utf-8", 'replace')
            except Exception, err:
                website=('Error while fetching website\n'+str(err)).encode('utf-8','replace')

            # author name	
            try:
                for link in soup.find_all('a'):
                    if(link.get('rel')=='author'):
                        author=(link.text).encode("utf-8", 'replace')
                #print author
            except Exception, err:
                author=('Error while fetching author name\n'+str(err)).encode('utf-8','replace')


            #story
            try:
                results = soup.findAll("div", {"class" : "Normal"})
                if(len(results)>0):
                    for div in results:
                        if (len(div)>1 and len(div.text)>2):
                             break
                        else:
                             continue
                    story=(div.text).encode("utf-8", 'replace')
                else:
                    results = soup.findAll("div", {"class" : "content"})
                    if len(results)>0:
                        story=results[0].text
                        story=story.encode('utf-8', 'replace')
                    else:
                        results = soup.findAll("p", {"class" : "blogSyn"})
                        if len(results)>0:
                            story=results[0].text
                            story=story.encode('utf-8', 'replace')
                        else:
                            results=soup.findAll('meta', name_='description')
                            story=results[0].get('content')
                            story=story.encode('utf-8', 'replace')
                story=story.replace('\n', ' ')
                story=story.replace('  ', '')
            except Exception, e:
                story=('Error while fetching story\n'+str(e)).encode('utf-8', 'replace')


            #insert into html table
            try:
                t.rows.append([title, author, website, story])
            except:
                print 'Error while inserting into html table'
        


        # write into output file
        try:
            opfile=str(url[i]).split('/')
            opfile=opfile[len(opfile)-3]
            opfile=opfile.strip()
            opfile=savedirClean+'/'+opfile+'.txt'
            if not os.path.isfile(opfile):
                if not os.path.exists(savedirClean):
                    os.makedirs(savedirClean)
                try:
                    with open(opfile, 'a+') as outfile:
                        outfile.write(str(t))
                        outfile.close()
                except:
                    with codecs.open(opfile, "a+", "utf-8") as outfile:
                        outfile.write(str(t))
                        outfile.close()
        except:
            print 'error while writing to file'


def Main():
    try:
        #variables initialize
        url=None

        #input file
        rf=open("crawler/et/et.txt", 'r')
        url=rf.readlines()
        #print url
        rf.close()

        #call scrape function
        scrape(url)
    except Exception, e:
        print e

if __name__ == '__main__':
    Main()

