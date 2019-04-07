import sys
from bs4 import BeautifulSoup
import HTML
import urllib
import datetime
import os.path
import codecs


def scrape(url):


    #flag initiate
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
    savedirDown='timesofindia/'+str(date)
    savedirClean='timesofindia/'+str(date)

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
        flag=int(flag)+1
        ff.close()
        ff=open(savedirClean+'/flag.txt', 'w+')
        ff.write(str(flag))
        ff.close()
    opfile=savedirClean+'/toi_op'+'_'+str(flag)+'.txt'
    

    for i in range(0,len(url),1):

        title=None
        website=None
        author=None
        story=None
        results=None
        y=None
        
        if len(url)>1:
            print (i+1)
            #print url[i]


            #html file download
            try:
                downfile=str(url[i]).split('/')
                downfile=downfile[len(downfile)-1]
                downfile=downfile.strip()
                downfile=savedirDown+'/'+downfile+'.html'
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
                results=soup.findAll('h1', {'itemprop' : 'headline'})
                if len(results)>0:
                    title=(results[0].text).encode("utf-8", 'replace')
                else:
                    results=soup.findAll('title')
                    title=(results[0].text).encode('utf-8', 'replace')
	        #print title
            except Exception, e:
                title=('Error while fetching title name\n'+str(e)).encode('utf-8', 'replace') 


            #website
            try:
                website=url[i].encode('utf-8', 'replace')
            except Exception, e:
                website=('Error while fetching website name\n'+str(e)).encode('utf-8', 'replace')


            # author name	
            try:
                results=soup.findAll('span', {'itemprop' : 'author'})
                author=(results[0].text).encode("utf-8", 'replace')
                #print author
            except Exception, e:
                author=('Error while fetching author name\n'+str(e)).encode('utf-8', 'replace')


            #story
            try:
                results = soup.findAll("div", {"class" : "article_content clearfix"})
                if len(results)>0:
                    story=(results[0].text).strip()
                else:
                    results=soup.findAll('div', class_='Normal')
                    if len(results)>0:
                        story=(results[0].text).strip()
                    else:
                        results=soup.findAll('span', class_='less_d')
                        if len(results)>0:
                            story=(results[0].text).strip()
                story=story.encode("utf-8", 'replace')
                story=story.replace("\n", ' ')
                story=story.replace('  ','')
	          #print story
            except:
                story=('Error while fetching story\n'+str(e)).encode('utf-8', 'replace')


            #insert into html table
            try:
                t.rows.append([title, author, website, story])
            except:
                print 'error while inserting into html table'
        else:
            break


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
        print 'Error while writing to file\n'+str(e)



def Main():
    try:
    	#variables initialize
        url=None


	#input file
        rf=open("toi.txt", 'r')
        url=rf.readlines()
        #print url
        rf.close()
        
        # call scrape
        scrape(url)
    except Exception, e:
        print e

if __name__ == '__main__':
    Main()
