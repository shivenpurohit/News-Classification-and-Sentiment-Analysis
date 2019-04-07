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
    if not os.path.exists(directory):
        #print ('Creating project '+directory)
        os.makedirs(directory)

# Create queue and crawled files (if not created)
def create_data_files(directory, linkFile):
    try:
        global opfile
        opfile=directory+'/'+linkFile
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
def savehtml(day, month, year, base_url, prefix, html_path):

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
    try:
        if (not os.path.isfile(html_path+'/'+day+'-'+month+'-'+year)):
            if not os.path.exists(html_path):
                os.makedirs(html_path)
            html=open(html_path+'/'+day+'-'+month+'-'+year, 'w')
            req=urllib2.Request(base_url+'print_dd='+day+'&print_mm='+month+'&print_yy'+year, headers={'User-Agent' : "Magic Browser"})
            htm=urllib2.urlopen(req)
            soup = bs4.BeautifulSoup(htm, 'html.parser')

            html=open(html_path+'/'+day+'-'+month+'-'+year, 'a+')
            html.write(soup.encode("utf-8", 'replace'))
            html.close()

            findnewslinks(soup, base_url, prefix, html_path)
    except Exception, err:
        print 'html error'
        print err

# find news links
def findnewslinks(soup, base_url, prefix, html_path):
    op=None
    try:
        results=soup.findAll('div', {'class':'topB'})
        if len(results)>0:
            for h in results:
                a=h.findAll('a')
                for link in a:
                    if(link.text!='More'):
                        url=link.get('href')
                        if(url.endswith('.htm') or url.endswith('.html')):
                            if(op is None):
                                op=prefix+url
                            else:
                                if not (prefix+url) in op:
                                    op=op+'\n'+prefix+url
            
            append_to_file(opfile, op)
    except Exception, e:
        print 'scraping error'
        print e



#call methods
print 
print '-----------------------------------------------------------------------------------------------------------------'
print 'Welcome To News Classification and Sentiment Analysis Application -- A project by Varuna Gupta and Shiven Purohit'
print '-----------------------------------------------------------------------------------------------------------------'
print

choice=raw_input('Do you want to start scraping of News Articles for Test data? (Y/N)  ')
print

#initialize global variables
global opfile
opfile=None 

if(choice == 'Y'):
    print
    choice=raw_input('Please select a news source to scrape\n1. Business Standard\n2. Economic Times\n')

    if(choice=='1'):
        directory='business-standard'
        base_url='http://www.business-standard.com/todays-paper?'
        prefix='http://www.business-standard.com'
        html_path=directory+'/html'

        print 'You have chosen Business Standard'
        create_project_dir(directory)
        create_data_files(directory, 'bs.txt')

        # start program
        try:
            date=raw_input('Please enter the date for which you want to scrape news items in YYYY-MM-DD format\n')
            date=date.split('-')
            savehtml(date[2], date[1], date[0], base_url, prefix, html_path)
        except Exception, e:
            print 'Error in start program\n'+str(e)

    elif(choice=='2'):
        directory='economic-times'
        base_url=''
        prefix=''
        html_path=directory+'/html'

        print 'You have chosen Economic Times'
        create_project_dir('economic-times')
        create_data_files('economic-times', 'et.txt')

         # start program
        try:
            date=raw_input('Please enter the date for which you want to scrape news items in YYYY-MM-DD format\n')
            date=date.split('-')
            savehtml(date[2], date[1], date[0])
        except Exception, e:
            print 'Error in start program\n'+str(e)

    else:
        print 'Invalid Choice'

else:
    print 'Application has been stopped by the user'


