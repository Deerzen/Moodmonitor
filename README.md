<div align=center>
<img src="https://raw.githubusercontent.com/Deerzen/Moodmonitor/main/logo.png" width="75%" height="75%">
</div>

## Easily conduct real-time sentiment & emotion analysis of Twitch chat

 Moodmonitor is an automated web-based IRC client which can connect to Twitch Chat and
 analyze the current sentiment and dominant emotions. The results of both
 sentiment & emotion analysis are visualized through charts on a web-dashboard.
 In a future version the generated data is supposed to be downloadable.

<div align=center>
<img src="https://raw.githubusercontent.com/Deerzen/Moodmonitor/main/preview.PNG" width="75%" height="75%">
</div>


## 🔍 Sentiment analysis with Afinn
 Moodmonitor uses the Afinn library (Nielsen 2011) to judge the sentiment of
 a message in chat and calculates averages in user defined intervals.
 Since the Afinn library is primarily designed for the English language, the script
 can only be used in English-speaking twitch communities.


## 🫂 Emotion analysis
 Emotes play a special role in communication in Twitch chat.
 However, a sentiment analysis with Afinn is unable to grasp this dimension.
 That is why Moodmonitor uses an innovative approach to analyze
 dominant emotions. The approach to classification is based on the
 psychological model "The Hourglass of Emotions" (Cambria, Livingstone, Hussain 2011).
 More specifically, the second-level emotions (ibid.: 153) have been used
 as categories. The most used emotes of Twitch and the popular browser extensions
 FZZ and BTTV (StreamElements 2021) have been assigned to the category that
 best matches their intended meaning respectively.
 The script counts how often emotes of a certain category have been used and
 reports what percentage of messages expressed the dominant emotion.
 
 This is a simple and effective approach that may cause problems with validity,
 not least because coding has been conducted by a single person. A survey that
 tries to identify the float values of "Pleasantness", "Attention", "Sensitivity"
 and "Aptitude" for every emote, which could be used to identify the associated
 second-level emotions more accurately seems like a costlier but superior approach
 (cf. Cambria, Livingstone, Hussain 2011: 151-152).

 Future versions of Moodmonitor will use the revisited version of
 the "Hourglass of Emotions" as a theoretical basis for emote classification
 (cf. Susanto et al. 2020: 97-100). Unlike the monitor the emote classifier scripts
 already use the improved model and the altered emotion dimensions.


## 📂 Explanation of the project structure
 The moodmonitor.py script accesses two files in the "JSON Files" folder.
 One stores the supplied OAuth Token and username. It will be created when you use
 the application for the first time. The other one contains the
 needed data for the emotion analysis in a JSON File. In the ML-Emote-Classifier folder
 I have provided optional scripts that might help with categorizing emotes on
 a regular basis.


## 🚩 Current problems regarding validity
 Since all emotes have been categorized by myself in 2020 there may be problems 
 regarding the validity of the generated emotion reports. The meaning of Twitch
 emotes may be ambiguous, it most likely changes over time and different contexts
 can have different connotations. The popular emote "OMEGALUL" i.e.
 is most commonly used to express gloat when a perceived failure occurs,
 but it could also be used to express genuine approval of a funny joke
 which would point towards optimism. All of these caveats are not addressed
 with the current hard coded approach to the classification of emotes.
 However, a machine learning algorithm may be capable of addressing
 these problems in the future. Alternatively, regular surveys of Twitch users
 could also be a worthwhile approach to solving these problems.


 ## 🤖 Optional machine learning scripts for categorization
To tackle the problem of not being able to categorize every emote regularly
I have provided optional scripts that should be able to do so. Based on supplied
training data they classify emotes on the four dimensions of pleasentness, attention,
sensitivity and aptitude over and over again. To predict the most likely value
for every dimension it uses linear regression. The results are saved locally
or in your own MongoDB collection provided they are statistically significant.
Based on the collected values the scripts categorize each emote
in the best fitting secondary emotion. The script automatically connects
to the most viewed twitch channels and runs each classifing operation in a seperate
process. Moodmonitor still needs to be updated to automatically use the generated data.  


## 🛫 How to start analyzing with Moodmonitor
1. Simply clone this repository, install requirements and run the script locally.
You can simply complete these steps by running:

```
git clone https://github.com/Deerzen/Moodmonitor.git
cd Moodmonitor
pip install -r requirements.txt
streamlit run moodmonitor.py
```
2. Alternatively, you can try out the app online:

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deerzen/moodmonitor/main/moodmonitor.py)


## 📚 Cited literature
 Cambira, Erik; Livingstone, Andrew; Hussain, Amir (2011): "The Hourglass of Emotions".
 In: Cognitive Behavioural Systems 2011, LNCS 7403, pp. 144–157.
 URL: https://sentic.net/hourglass-of-emotions.pdf

 Nielsen, Finn Årup (2011): "A new ANEW: evaluation of a word list
 for sentiment analysis in microblogs", Proceedings of the ESWC2011 Workshop
 on 'Making Sense of Microposts': Big things come in small packages.
 Volume 718 in CEUR Workshop Proceedings: 93-98. Matthew Rowe, Milan Stankovic,
 Aba-Sah Dadzie, Mariann Hardey (editors)
 URL: http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/6006/pdf/imm6006.pdf

 StreamElements (2021): "StreamElements Chat Stats - Recording dank memes from
 Twitch Chat since, January 9th 2016". URL: https://stats.streamelements.com/c/global

 Susanto, Yospehine; Livingstone, Andrew G.; Ng, Bee Chin; Cambira Erik (2020):
 "The Hourglass Model Revisited". In: IEEE Intelligent Systems, 35.5, p. 96-102.
