# Moodmonitor

 Moodmonitor is an automated IRC client which can connect to Twitch Chat and
 analyse the current sentiment and dominant emotions.

 To use the Client you will need an OAuth password which is associated to
 a Twitch account and can be generated at https://twitchapps.com/tmi/

 moodbarometer.py uses the Afinn library to judge the sentiment of
 a message in chat and calculates averages in user defined intervals.
 Since the Afinn library is designed for the English language the script
 can only be used in English speaking twitch communities.

 Emotes play a special role in the communication in Twitch chat.
 However, a sentiment analysis with Afinn is unable to grasp this dimension.
 That is why moodbarometer.py uses an innovative approach of analysing
 dominant emotions. The approach to classification is based on the
 psychological model "The Hourglass of Emotions" (Cambria, Livingstone, Hussain 2011).
 More specifically the second-level emotions (ibid.: 153) have been used
 as categories. The most used emotes of Twitch and the popular browser extensions
 FZZ and BTTV (StreamElements 2021).
 have been assigned to the category that best matches its intended meaning.
 The script counts how often emotes of a certain category have been used and
 reports what percentage of messages expressed the dominant emotion.

 This is a simple and effective approach that may cause problems with validity
 not least because coding has been conducted by a single person. A survey that
 tries to identify the float values of "Pleasantness", "Attention", "Sensitivity"
 and "Aptitude" for every emote, which could be used to identify the associated
 second-level emotions more accurately seems like a costlier but superior approach
 (cf. Cambria, Livingstone, Hussain 2011: 151-152).

 The moodbarometer.py script generates two files in the working directory.
 One stores the supplied OAuth Token and username. The other one saves
 the generated reports in a JSON File. The second script graphsentiment.py tries
 to access the generated JSON file and uses the Matplotlib library to graph
 the recorded data points of the sentiment analysis live. Currently
 graphsentiment.py might crash when it tries to read the recorded data while moodbarometer.py is writing to the file.


 Cambira, Erik; Livingstone, Andrew; Hussain, Amir (2011): "The Hourglass of Emotions".
 In: Cognitive Behavioural Systems 2011, LNCS 7403, pp. 144–157.
 URL: https://sentic.net/hourglass-of-emotions.pdf

 StreamElements (2021): "StreamElements Chat Stats - Recording dank memes from
 Twitch Chat since, January 9th 2016". URL: https://stats.streamelements.com/c/global
