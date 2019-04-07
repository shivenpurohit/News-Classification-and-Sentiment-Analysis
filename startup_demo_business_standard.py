import os

cwd = os.path.join(os.getcwd(), "crawler/business-standard.py")
os.system('{} {}'.format('python', cwd))

cwd = os.path.join(os.getcwd(), "scraper/business_standard.py")
os.system('{} {}'.format('python', cwd))

cwd = os.path.join(os.getcwd(), "Autosummarize/autosummarize.py")
os.system('{} {}'.format('python', cwd))

cwd = os.path.join(os.getcwd(), "classification/classification_multi.py")
os.system('{} {}'.format('python', cwd))

cwd = os.path.join(os.getcwd(), "Sentiment/senti_nb.py")
os.system('{} {}'.format('python', cwd))