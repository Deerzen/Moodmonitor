<div align=center>
<img src="https://raw.githubusercontent.com/Deerzen/Moodmonitor/main/logo.png" width="50%" height="50%">
</div>

## Easily perform Twitch chat sentiment & emotion analysis in real-time

 Moodmonitor is an automated web-based IRC client which can connect to Twitch Chat and
 analyse the current sentiment and dominant emotions. The results of both
 the sentiment & emotion  analysis are visualized through charts on a web-dashboard.
 In a future version the generated data is supposed to be downloadable.

<div align=center>
<img src="https://raw.githubusercontent.com/Deerzen/Moodmonitor/main/preview.PNG" width="50%" height="50%">
</div>


## 🔍 Sentiment analysis with Afinn
 moodmonitor.py uses the Afinn library (Nielsen 2011) to judge the sentiment of
 a message in chat and calculates averages in user defined intervals.
 Since the Afinn library is primarily designed for the English language the script
 can only be used in English speaking twitch communities.


## 🫂 Emotion analysis
 Emotes play a special role in the communication in Twitch chat.
 However, a sentiment analysis with Afinn is unable to grasp this dimension.
 That is why moodmonitor.py uses an innovative approach of analysing
 dominant emotions. The approach to classification is based on the
 psychological model "The Hourglass of Emotions" (Cambria, Livingstone, Hussain 2011).
 More specifically the second-level emotions (ibid.: 153) have been used
 as categories. The most used emotes of Twitch and the popular browser extensions
 FZZ and BTTV (StreamElements 2021) have been assigned to the category that
 best matches their intended meaning respectively.
 The script counts how often emotes of a certain category have been used and
 reports what percentage of messages expressed the dominant emotion.
 
 This is a simple and effective approach that may cause problems with validity
 not least because coding has been conducted by a single person. A survey that
 tries to identify the float values of "Pleasantness", "Attention", "Sensitivity"
 and "Aptitude" for every emote, which could be used to identify the associated
 second-level emotions more accurately seems like a costlier but superior approach
 (cf. Cambria, Livingstone, Hussain 2011: 151-152).


## 📂 Explanation of the project structure
 The moodmonitor.py script accesses two files in the "JSON Files" folder.
 One stores the supplied OAuth Token and username. The other one contains the 
 needed data for the emotion analysis in a JSON File.


## 🛫 How to start analyzing with Moodmonitor
1. Clone this repository and install requirements by simply running:

```
git clone https://github.com/Deerzen/Moodmonitor.git
cd Moodmonitor
pip install -r requirements.txt
```
2. To use the client you will need an OAuth password which is associated to
a registered Twitch account. It can be easily generated at https://twitchapps.com/tmi/

3. Open the folder "JSON Files" and create a file named config.json - add an array
to the file and enter your OAuth password and associated twitch user-name:

```
["generated oauth password", "associated user-name"]
```

4. You are now set to run the app:

```
streamlit run moodmonitor.py
```


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
