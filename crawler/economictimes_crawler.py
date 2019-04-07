import os
import bs4
import urllib2
import urllib
import codecs
import socket
import re
import datetime
import time

# Each website we crawl is a seperate folder
def create_project_dir(directory):
    if not os.path.exists(directory	):
        print ('Creating project '+directory)
        os.makedirs(directory)

# Create queue and crawled files (if not created)
def create_data_files():
    try:
        global opfile
        opfile=directory+'/et.txt'
        if not os.path.isfile(opfile):
            write_file(opfile, '')
    except Exception, e:
        print 'Error while creating data files\n'+str(e)


# write data
def write_file(path, data):
    try:
        with codecs.open(path, "w", "utf-8") as outfile:
            outfile.write(str(data))
            outfile.close()
    except Exception, e:
        print 'Error while writing file\n'+str(e)

# Add data onto an existing file
def append_to_file(path, data):
    try:
        with open(path, 'r+') as file:
            content=file.read()
            file.seek(0, 0)
            file.write(data.strip()+"\n"+content)
            file.close()
    except Exception, e:
        print 'Error while appending to file\n'+str(e)


# save html file
def savehtml(currentDate, day, month, year):

    global flag
    global base_url
    global html_path
    global startDate

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Connection': 'keep-alive'}
    try:
        if (not os.path.isfile(html_path+'/'+str(currentDate)) or currentDate==startDate ):
            if not os.path.exists(html_path):
                os.makedirs(html_path)
            html=open(html_path+'/'+str(currentDate), 'w')
            print base_url+'archivelist/year-'+str(year)+',month-'+str(month)+',starttime-'+str(day).strip()+'.cms'
            req=urllib2.Request(base_url+'archivelist/year-'+str(year)+',month-'+str(month)+',starttime-'+str(day).strip()+'.cms', headers={'User-Agent' : "Magic Browser"})
            htm=urllib2.urlopen(req)
            soup = bs4.BeautifulSoup(htm, 'html.parser')

            html=open(html_path+'/'+str(currentDate), 'a+')
        html.write(soup.encode("utf-8", 'replace'))
        html.close()

        findnewslinks(soup)
    except Exception, err:
        print 'html error'
        print err

# find news links
def findnewslinks(soup):
    global op
    global flag
    global prefix
    try:
        results=soup.findAll('ul', {'class':'content'})
        if len(results)>0:
            for h in results:
                a=h.findAll('a')
                for link in a:
                    url=link.get('href')
                    if(op is None):
                        op=prefix+url
                    else:
                        if not (prefix+url) in op:
                            op=op+'\n'+prefix+url
            
            global i
            if flag==0:
                pass
            else:
                append_to_file(opfile, op)
    except Exception, e:
        print 'scraping error'
        print e



directory='Z:/end to end crawler/Crawler/et'

#initialize variables
global base_url
base_url='http://economictimes.indiatimes.com/archivelist/'
global prefix
prefix='http://economictimes.indiatimes.com'
global opfile
opfile=None
global html_path
html_path=directory+'/html' 
global last_link
progress_url=None
global flag
flag=0
global op
op=None
global i


#call methods
create_project_dir(directory)
create_data_files()


#end date
try:
    ff=open('flag_et.txt', 'r')
    startDate=ff.readlines()
    day=startDate[1]
    startDate=time.strptime(startDate[0].strip(),"%Y-%m-%d")
    startDate=datetime.date(startDate.tm_year,startDate.tm_mon,startDate.tm_mday)
    ff.close()
    
    endDate=datetime.datetime.today()
    endDate=str(endDate).split(' ')
    endDate=endDate[0]
    endDate=time.strptime(endDate,"%Y-%m-%d")
    endDate=datetime.date(endDate.tm_year,endDate.tm_mon,endDate.tm_mday)
except Exception, e:
    print 'Error while fetching current date\n'+str(e)


# start program
try:
    global i
    currentDate=startDate
    print currentDate
    while(flag==0):

        month=currentDate.month
        year=currentDate.year

        if(str(currentDate)!=str(endDate)):
            savehtml(currentDate, day, month, year)
        else:
            flag=1
            savehtml(currentDate, day, month, year)
            break
        currentDate=currentDate+datetime.timedelta(1)
        day=int(day)+1
        print currentDate

    ff=open('flag_et.txt', 'w')
    ff.write(str(endDate))
    ff.write('\n'+str(day))
    ff.close()
except Exception, e:
    print 'Error in start program\n'+str(e)



