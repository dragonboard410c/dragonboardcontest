#!/usr/bin/python
from temboo.Library.Dropbox.FilesAndMetadata import UploadFile
from temboo.core.session import TembooSession
import telegram
import cv2, os
import numpy as np
from PIL import Image
from time import gmtime, strftime
import base64
import sys
import time
from threading import Thread

INTERVAL = 1
os.environ["ALSA_CARD"]="1"

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# LBPH Face Recognizer 
recognizer = cv2.createLBPHFaceRecognizer()

#setup tg
bot = telegram.Bot(token='785465824:ABcdryghdkrsRWuM51_TP5BGnNNJoCyBu8')

start_surv = 0
update_id = 0
chat_id = 0

def create_database():
    path = './faces'
    im_paths = [os.path.join(path, f) for f in os.listdir(path)]
    images = []
    labels = []
    index = 0
    for im_path in im_paths:
        # Read the image
        im_pil = Image.open(im_path)
        #convert image into grayscale
        im_pil = im_pil.convert('L')
        # Convert the image format into numpy array
        im = np.array(im_pil, 'uint8')
        # image index
        index = index + 1
        # Detect the face in the image
        faces = faceCascade.detectMultiScale(im)
        # If face is detected, append the face and index
        for (x, y, w, h) in faces:
            images.append(im[y: y + h, x: x + w])
            labels.append(index)
    # return the lists
    return images, labels
    
def send_message(id, message):
    bot.sendMessage(chat_id=id, text=message)
    
def parse_message():
    global start_surv
    global update_id
    global chat_id
    
    while 1:
        for update in bot.getUpdates(offset=update_id, timeout=10):
            invalid_cmd = 0
            update_id = update.update_id + 1
            message = update.message.text
            #print(message)

            if message:
                # Reply to the message
                cmd = message.upper().split(' ')
                #print cmd
                #print len(cmd)
                if cmd[0] == 'BOT':
                    if len(cmd) < 3:
                        invalid_cmd = 1
                    else:
                        if cmd[1] == 'SURV':
                            if cmd[2] == 'ON':
                                start_surv = 1
                                #print "surveillance started" 
                            elif cmd[2] == 'OFF':
                                start_surv = 0
                                #print "surveillance stopped" 
                            else:
                                invalid_cmd = 1
                        elif cmd[1] == 'MSG':
                            #print message[8:]
                            os.system('espeak -s 115 -v en+m3 -p 25 "' + message[8:] + '"')
                else:
                        invalid_cmd = 1
                        
            if invalid_cmd == 1:
                send_message(chat_id, "Invalid command")
                          
    return 
    
def image_capture_n_process():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3,640)
    video_capture.set(4,480)
    
    # Create a session with your Temboo account details
    session = TembooSession("dragonboard_1", "myFirstApp", "7854856485e94b5ab4633e8a3af31bcc")
    
    # Instantiate the Choreo
    uploadFileChoreo = UploadFile(session)

    # Get an InputSet object for the Choreo
    uploadFileInputs = uploadFileChoreo.new_input_set()

    # Set credential to use for execution
    uploadFileInputs.set_credential('dbupload')
    
    frame_t = video_capture.read()[1]
    frame_t = video_capture.read()[1]
    frame = frame_t
    frame_gray = cv2.cvtColor(frame_t, cv2.COLOR_RGB2GRAY)
    frame_t = cv2.blur(frame_gray, (3, 3))
    frame_t_minus = frame_t
    upload_time = 0

    while (1):
        
        
        #print "SS: ", start_surv
        
        if start_surv == 1:
            #print "capture and compare"		
            filename = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '.jpg';
                
            frame_delta = cv2.absdiff(frame_t_minus, frame_t)
            frame_delta = cv2.threshold(frame_delta, 12, 255, 3)[1]
            delta_count = cv2.countNonZero(frame_delta)
            #print "dc: ", delta_count

            if delta_count > 10:
                # Capture frame-by-frame
                faces = faceCascade.detectMultiScale(frame_gray)
                for (x, y, w, h) in faces:
                    X, conf = recognizer.predict(frame_gray[y: y + h, x: x + w])
                    print "confidence: ", conf
                    if conf > 200:      #confidence threshold
                        if (upload_time + INTERVAL) < time.time():
                            upload_time = time.time()
                            cv2.imwrite('capture.jpg',frame) 
                            bot.sendPhoto(chat_id=chat_id, photo=open('capture.jpg', 'rb'))
                            uploadFileInputs.set_FileName(filename)
                            with open('capture.jpg', "rb") as image_file:
                                encoded_string = base64.b64encode(image_file.read())
                            uploadFileInputs.set_FileContents(encoded_string)
                            # Execute the Choreo
                            uploadFileResults = uploadFileChoreo.execute_with_results(uploadFileInputs)
                    
            # Advance the frames.
            frame_t_minus = frame_t
            frame_t = video_capture.read()[1]
            frame = frame_t
            frame_gray = cv2.cvtColor(frame_t, cv2.COLOR_RGB2GRAY)
            frame_t = cv2.blur(frame_gray, (3, 3))
    # When everything is done, release the capture
    video_capture.release()

def main():
    global update_id
    global start_surv
    global chat_id
    
    images, labels = create_database()

    # Perform the tranining
    recognizer.train(images, np.array(labels))
    
    # setup telegram
    chat_id = bot.getUpdates()[-1].message.chat_id
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None
    
    im_thread = Thread(target=image_capture_n_process)
    im_thread.start()
    
    tg_thread = Thread(target=parse_message)
    tg_thread.start()
    
    #print "System Ready!!!"
    
    while 1:
        i = 1
    
if __name__ == '__main__':
    main()
