# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 20:48:24 2018

@author: hari
"""
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream, FPS, VideoStream
from imutils import face_utils
import imutils
import argparse
import numpy as np
import time
import dlib
import cv2

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.lang.builder import Builder

Builder.load_string('''
<Button>:
    background_normal: ''
    canvas.before:
        Color:
            rgba: (1,1,1,1)
        Line:
            width: 2
            rectangle: self.x, self.y, self.width, self.height
    background_color: (0.05,0.5,0.8,1)
    font_size: 40
    color: 1,1,1,1
    size_hint: 0.2, 0.1
<Layout>:
        
    orientation: 'vertical'

    canvas.before:
        Color:
            rgba:0.05, 0.5, 0.8,1
        Rectangle:
            pos: self.pos
            size: self.size    
    Image:
        id: img
        size: 20,20
    Button:
        border: 0,0,0,0
        id: blink
        text: "Blink"
        pos_hint: {'x':.1, 'y':.2}
        on_press: root.onCameraClick()
    Button:
        id: next
        text: "Exit"
        pos_hint: {'x':.7, 'y':.2}
    Label:
        id: label
        text: "Take a Blink Selfie..!"
        pos_hint: {'x':.8, 'y':.3}
''')

class Layout(FloatLayout):
    def onCameraClick(self, *args):
        #blink = self.ids['blink']
        #camera = self.ids['camera']
        #camera.play = True
        #camera.export_to_png("C:/Hari Docs/Kivy/pic.png")
        #print('Picure Taken')
        image = self.ids['img']
        
        def eye_aspect_ratio(eye):
            A = dist.euclidean(eye[1], eye[5])
            B = dist.euclidean(eye[2], eye[4])
            C = dist.euclidean(eye[0], eye[3])
            ear = (A + B) / (2.0 * C)
            return ear
        
        EYE_AR_THRESH = 0.3
        EYE_AR_CONSEC_FRAMES = 3
         
        # initialize the frame counters and the total number of blinks
        COUNTER = 0
        TOTAL = 1
        
        shape_predictor = 'F:/Data_Science/FaceRecognition/shape_predictor_68_face_landmarks.dat'
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(shape_predictor)
        
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']
        
        print("[INFO] starting video stream thread...")
        vs = VideoStream(src=0).start()
        fileStream = False
        time.sleep(1.0)
        #fps= FPS().start()
        cv2.namedWindow('Capture', cv2.WINDOW_NORMAL)
        flag = 1
        while (flag == 1):
            frame = vs.read()
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         
            rects = detector(gray, 0)
            
            for rect in rects:
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
         
                ear = (leftEAR + rightEAR) / 2.0
                
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                
                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                else:
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        print('Blink detected, stay steady and look at the camera...!')
                        #while TOTAL <= 3:
                        frame = vs.read()
                        time.sleep(5) 
                        img_name =  'opencv_frame_{}.png'.format(TOTAL)
                        cv2.imwrite(img_name, frame)    
                        print('{} written'.format(img_name))
                        #TOTAL += 1                                               
                        #fps.stop()
                        #vs.stream.release()
                        flag = 0                        
                    COUNTER = 0  # reset the eye frame counter
            cv2.imshow('Capture', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        vs.stop()
        cv2.destroyAllWindows()        
        #label = self.ids['label']
        #label.text = 'Picture Taken'        
        image.source = img_name

class myKivy(App):
    def build(self):
        
        return Layout()

if __name__=='__main__':
    myKivy().run()
