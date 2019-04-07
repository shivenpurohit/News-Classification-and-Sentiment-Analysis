import sys
from bs4 import BeautifulSoup
import HTML
import urllib
import datetime
import os.path
import codecs


def scrape(url):


    #flag initiation
    flag=0
    
    #html table initialize
    try:
        t = HTML.Table(header_row=['Title', 'Author', 'Website', 'Story'])
    except:
        print 'Error while initializing html table'
    #print t

    # find current date
    try:
        date=datetime.datetime.now().strftime ("%d-%m-%Y")
    except Exception, e:
        print 'Error while fetching current date\n'+str(e)
    
    #output file initialize
    savedirDown='thehindu/'+str(date)
    savedirClean='thehindu/'+str(date)

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
    opfile=savedirClean+'/thehindu_op'+'_'+str(flag)+'.txt'
    
    for i in range(0, len(url), 1):
        flag=None
        title=None
        website=None
        author=None
        story=None
        results=None
        y=None
        print (i+1)
       # print url[i]

        #create html source file
        try:
            downfile=str(url[i]).split('/')
            downfile=downfile[len(downfile)-2]
            downfile=downfile.strip()
            downfile=savedirDown+'/'+downfile
            if not os.path.isfile(downfile):
                if not os.path.exists(savedirDown):
                    os.makedirs(savedirDown)
                htm = urllib.urlopen(url[i])
                soup = BeautifulSoup(htm, 'html.parser')
                df=open(downfile, 'a+')
                df.write(soup.encode("utf-8", 'replace'))
                df.close()
            else:
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
                    title=link.get('content')
                    title=title.encode('utf-8', 'replace')
        except Exception, e:
            title=('Error while fetching title name\n'+str(e)).encode('utf-8', 'replace') 


        #website
        try:
            website=url[i].encode('utf-8', 'replace')
        except Exception, e:
            website=('Error while fetching website\n'+str(e)).encode('utf-8', 'replace')


        # author name	
        try:
            for link in soup.find_all('meta'):
                if(link.get('name')=='author'):
                    #print link.get('content')
                    author=(link.get('content')).encode('utf-8', 'replace')
        except Exception, e:
            author=('Error while fetching author name\n'+str(e)).encode('utf-8', 'replace')


        #story
        try:
            results = soup.findAll("p", {"class" : "body"})
            for p in results:
                if story is None:
                    story=p.text
                    story=story.encode('utf-8', 'replace')
                    story=story.strip()
                else:
                    y=(p.text).encode('utf-8', 'replace')
                    story=story+y    
            story=story.replace('\n', ' ')
            story=story.replace('  ', '')
        except Exception, e:
            story=('Error while fetching story\n'+str(e)).encode('utf-8', 'replace')


        #insert into html table
        try:
            t.rows.append([title, author, website, story])
        except:
            print 'error while inserting into html table'
        #print t

    # write into output file
    try:
        if not os.path.isfile(opfile):
            if not os.path.exists(savedirClean):
                os.makedirs(savedirClean)
            try:
                with open(opfile, 'w') as outfile:
                    outfile.write(str(t))
                    outfile.close()
            except:
                with codecs.open(opfile, "w", "utf-8") as outfile:
                    outfile.write(str(t))
                    outfile.close()
    except Exception, e:
        print 'Error while writing to a file\n'+str(e)
    


def Main():
    try:
        #variables initialize
        url=None


        #input file
        rf=open("thehindu.txt", 'r')
        url=rf.readlines()
        #print url
        rf.close()

        # call scrape method
        scrape(url)
    except Exception, e:
        print e

if __name__ == '__main__':
    Main()


