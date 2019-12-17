 [![pipeline status](http://gitlab.tredence.com:10080/root/sttc/badges/dec_demo/pipeline.svg)](http://gitlab.tredence.com:10080/root/sttc/commits/dec_demo)
# Text and Audio Capabilities - TAAC
This repository contains capabilities with focus on Text and Audio. App folder contains code to show the demo of the capabilities built using webpage UI.
* Audio capabilities
  * Sentiment analysis of the audio calls
  * Transcription of the audio (ASR)
* Text capabilities
  * Sentiment analysis of the text
  * Topics/Themes generation from the text
  
# Usage Instructions
1. Clone the repository
2. Install all the modules in the python environment using requirements.txt
3. To test the specific capability use it's readme.
4. To index data on ElasticSearch, open terminal and run command "python App/Themes/Index_Data.py" and enter the directory path where all dataset files are located.

	**Dataset File Structure Sample**:</br>
	amazon_reviews dataset - "This Kindle is an excellent buy" &ensp; (1 column -- verbatim)</br>
	walmart_openend dataset - "Problem with walmart store" &ensp; (1 column -- verbatim)</br>
	ecolab_calls dataset - "Export Steve here. How's work?", 20191176333838363 &ensp; (2 columns -- verbatim, filename)</br>
	marriott_calls dataset - 06-01-27_sid_133, "Thank you for calling Marriott" &ensp; (2 columns -- filename, verbatim)</br>
	
5. **Use the current directory** to test the demo using the command in the terminal "python App/app.py"


# Folder Structure
* App
    * app.py
* Audio
    * SpeechToText
    * SpeechSentiment
* Text
    * TextSentiment
    * ThemeGeneration


# Maintainers
1. Shubham Pandey
2. Siddharth Shukla
3. Shiven Purohit
