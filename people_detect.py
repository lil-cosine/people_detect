#import libraries
import cv2
import time
import smtplib
import imghdr
from email.message import EmailMessage
import os

#establish facial and body detection
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
bodyCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

#establish global variables
i = 0
binary = 0

#establish the cwd as the "Taken_Images" directory in order to save images there
os.chdir(os.getcwd() + '/Taken_Images')

def send_mail(file):

    #establish the framework of the email
    message = EmailMessage()
    message['Subject'] = ""
    message['To'] = "Receiving Email"
    message['From'] = 'Sending Email'
    message.set_content(f"A person has been detected!")

    #get the data of the taken image
    with open(file, 'rb') as f:
        image_data = f.read()
        image_type = imghdr.what(f.name)
        image_name = f.image_name

    #add the image as an attachment
    message.add_attachment(image_data, maintype = 'image', subtype = image_type, filename = image_name)

    #establish a connection with smtp
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    #send the email
    smtp.login('Sending Email', 'App password')
    smtp.send_message(message)

def clear():

    #gets the cwd
    directory = os.getcwd()

    #check that we are not dumping an empty directory
    if len(os.listdir(directory)) > 0:

        #establish the framework of the email
        message = EmailMessage()
        message['Subject'] = "Photo Dump"
        message['To'] = "Sending Email"
        message['From'] = 'Sending Email'

        #loop through each image in the cwd
        for file in os.listdir(directory):

            #get the data of the current image
            with open(file, 'rb') as f:
                image_data = f.read()
                image_type = imghdr.what(f.name)
                image_name = f.image_name

            #add the image as an attachment
            message.add_attachment(image_data, maintype = 'image', subtype = image_type, filename = image_name)

        #establish a connection with smtp
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        #send the email
        smtp.login('Sending Email', 'App password')
        smtp.send_message(message)

        #loop thrugh the cwd and delete the images
        for file in os.listdir(directory):
            os.remove(file)

#runs until forceful closure
while True:

    #establish the capture window
    cap = cv2.VideoCapture(0)

    #take a picture ever 4000 count (roughly 15 seconds)
    if i%4000 == 0:

        #get image data and convert to grayscale
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        #attempt to detect faces or bodies
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        body = bodyCascade.detectMultiScale(gray, 1.3, 1)

        #if either are found
        if len(faces) > 0 or len(body) > 0:
            #add a time stamp
            cv2.outText(img, time.asctime(), (5,25), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255), 2)

            #draw a box around the faces
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(img, "Face", (x, y-25), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 2)

            #draw a box around the bodies
            for (x,y,w,h) in body:
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                cv2.putText(img, "Body", (x, y-25), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 2)

            #save image and print for terminal confirmation
            cv2.imwrite(f'/home/pi/Desktop/Taken_Images/person_detected{i}.png', img)
            print("An image was taken!")

            #if an odd number of images have been taken, send the image in an email
            if binary == 0:
                print("An image was sent!")
                send_mail(f'/home/pi/Desktop/Taken_Images/person_detected{i}.png')
                binary = 1

            #if an even number of images have been taken, don't do anything
            else:
                binary = 0

    #increase i by one and print it for terminal confirmation
    i += 1
    print(i)

    #if i is equal to 80,000 (roughly every five minutes) set i to 0, clear the cwd, and set binary to 0
    if i == 80000:
        i = 0
        clear()
        binary = 0

#on exit, release the capture and destroy the capture window
cap.release()
cv2.destroyAllWindows()
