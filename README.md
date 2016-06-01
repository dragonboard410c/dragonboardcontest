# dragonboardcontest
My entry for dragonboard contest

Idea is to have a surveillance system with sends only "sensible" alerts/notifications. This is achieved my examining captured image for already known "entities". DragonBoard410c is coupled with USB camera and USB audio card. USB camera for capturing images and USB audio card to read out messages sent by user over Telegram IM. For analyzing images OpenCV is used. If the image captured is unknown to the system, image is sent to user over telegram and is simultaneously uploaded to dropbox. To achieve dropbox functionality, Temboo framework is used. If user wants to send an audio message to the intruder, he can do it by using Telegram and Dragonboard410c will convert text message to speech and output it to USB audio card.

#How it works...
On boot-up main application, main.py is run. The application first sets up OpenCV for face detection and recognition, creates database of known entities. These entities can be anything, for our usecase we are storing face images in "faces" folder. OpenCV trainer fetches all the images from "faces" folder and trains the recognizer. Main application initializes Telegram bot with token and chat_id. Finally two threads are created, one for handling incoming Telegram messages and other for handling camera capture and processing. "espeak" is used to convert text to speech. FTP server on Dragonboard410c is used to upload/delete permitted uses' face images.

*Image processing thread:*
This thread initalizes Temboo framework for dropbox upload, sets capture resolution to 640x480, captures image and checks for any movement, if movement is detected, face detection is tried on that image, if face is detected, image is given to recognizer engine to match it against all the known entities. If face is not detected or recognized, that image is sent to user over Telegram IM and is uploaded to dropbox with name as timestamp.

*Telegram message parser:*
This thread receives incoming messages, parses it and takes appropriate action. Below is the command format,
"Bot \<cmd\> \<action/message\>"

For triggering text to speech,

    "Bot msg who are you?"

For surveillance turn on/off,

    "Bot surv on"
 
    "Bot surv off"

Currently only above 3 commands are supported. If anything other than above commands is sent, Dragonboard410c replies with "Invalid Command".

#Preparing DragonBoard410c
Flashing Debian: https://github.com/96boards/documentation/wiki/Dragonboard-410c-Installation-Guide-for-Linux-and-Android

Install python-telegram-bot: *sudo pip install python-telegram-bot --upgrade*

Install espeak: *sudo apt-get install espeak*

Install vsftpd for uploading/deleting user faces for face recognition. Configure it to access only "faces" folder: *sudo apt-get install vsftpd*

Download Temboo python framewok and place it along with "main.py". For information on authorization required for dropbox operations, visit https://temboo.com

Install Python-OpenCV: *sudo apt-get install python-opencv*

#Running main application
*python main.py*

Dragonboard410c can be configured to run this application soon after bootup.



