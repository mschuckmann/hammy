import cv2 as cv
import numpy as np
from operator import itemgetter
from datetime import timedelta

class VideoPlayer:
    def __init__(self, path, enable_mouse = True, window_name = None, gBlur = False):
        if not window_name:
            self.win_name = path
        else:
            self.win_name = window_name

        print( "gBlur = {0}".format(gBlur) )
        self.gaussianBlur = gBlur
        if self.gaussianBlur:
            print( "GUASIANBLUR is on" )
        self.path = path
        self.regions = []
        self.cap = cv.VideoCapture(path)
        self.position = 0
        self.seek(0)
        self.text = ""
        self.frame = None
        

        cv.namedWindow(self.win_name, cv.WINDOW_AUTOSIZE)
        if enable_mouse:
            cb = (lambda event, x, y, flags, param: self.clip_and_crop(event,x,y,flags,param))
            cv.setMouseCallback(self.win_name, cb)

    def release(self):
        self.cap.release()
        cv.destroyWindow(self.win_name)
        
    def draw(self):
        if self.frame is not None:
            temp = self.frame.copy()
            for r in self.regions:
                cv.rectangle(temp, r[0], r[1], (0,255,0),2)
            text = "{0},{1}".format(str(timedelta(milliseconds=self.get_pos())),self.text) 
            cv.putText(temp, text, (100,50), cv.FONT_HERSHEY_SIMPLEX, 2, (0,255,0))
            cv.imshow(self.win_name,temp)

    def next(self):
        ret, self.frame = self.cap.read()
        if ret:
            if self.gaussianBlur:
                self.frame = cv.GaussianBlur(self.frame, (21, 21), 0)
            self.frame = cv.resize(self.frame, (0,0), fx=0.5, fy=0.5 )
        self.position = self.cap.get(cv.CAP_PROP_POS_MSEC)
        return ret
             
    def step( self, msec = 500 ):
        self.position += msec
        self.cap.set(cv.CAP_PROP_POS_MSEC, self.position)
        return self.next()

    def seek(self, msec ):
        self.position = msec
        self.cap.set(cv.CAP_PROP_POS_MSEC, self.position)
        return self.next()

    def set_text( self, text ):
        self.text = text
        
    def add_region(self, refPt):
        self.regions.append(refPt)
        self.draw()

    def pop_region(self):
        if self.regions:
            self.regions.pop()
        self.draw()
            
    def clear_regions(self):
        self.regions = []
        self.draw()

    def get_regions(self):
        return self.regions
    
    def get_pos(self):
        return self.position #self.cap.get(cv.CAP_PROP_POS_MSEC)

    def clip_and_crop(self, event, x, y, flags, param ):
        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being
        # performed
        if event == cv.EVENT_LBUTTONDOWN:
            self.regions.append([(x, y)])

        # check to see if the left mouse button was released
        elif event == cv.EVENT_LBUTTONUP:
            
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            self.regions[-1].append((x, y))
            r = self.regions[-1]
            # we need to make sure the region is upper left to lower right
            self.regions[-1] = [(min(r[0][0],r[1][0]), min(r[0][1],r[1][1])),
                                (max(r[0][0],r[1][0]), max(r[0][1],r[1][1]))]
            print ("region:{0}".format(r))
            self.draw()

        
        
