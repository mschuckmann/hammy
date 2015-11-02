import numpy as np
import cv2


class Crop:
    def __init__( self, name, x, w, y, h ):
        self.N = name
        self.X = x
        self.W = w
        self.Y = y
        self.H = h
        self.ref = None
        self.crop = None

crops = [ Crop('r1', 0, 2000, 300, 1500),
          Crop('r2', 0, 1650, 400, 150) ]

step_ms=500
ref_frame_pos_ms=1000*20
x_scale=0.5
y_scale=0.5
threshold=30

f = 'c:\\builds\\opencv\\hammy\\left.mp4'
#f = 'f:\\Videos\\PW03\\20151010-PDX3-WH5\\orig\\left\\GOPR0114.MP4'
#f = 'f:\\test.avi'
cap = cv2.VideoCapture(f)

#Seek to the refernce frame.
cap.set(cv2.CAP_PROP_POS_MSEC, ref_frame_pos_ms )

ret, ref = cap.read()
if ret:
    for c in crops:
        c.ref = ref[c.Y:c.Y+c.H, c.X:c.X+c.W]
        c.ref = cv2.cvtColor(c.ref, cv2.COLOR_BGR2GRAY)
        c.ref = cv2.resize(c.ref, (0,0), fx=x_scale, fy=y_scale )

capturing = False
startTime = None
pos = 1000*0
cap.set(cv2.CAP_PROP_POS_MSEC, pos )
cv2.namedWindow( "thumb" )
cutlist = []

while(1):
    cap.set(cv2.CAP_PROP_POS_MSEC, pos + step_ms )
    pos = cap.get(cv2.CAP_PROP_POS_MSEC)
    ret, frame = cap.read()
    if not ret:
        break;

    for c in crops:
        c.crop = frame[c.Y:c.Y+c.H, c.X:c.X+c.W]
        c.crop = cv2.cvtColor(c.crop, cv2.COLOR_BGR2GRAY)
        c.crop = cv2.resize(c.crop, (0,0), fx=x_scale, fy=y_scale )
        c.crop = cv2.absdiff( c.ref, c.crop )
        a, c.crop = cv2.threshold(c.crop, threshold, 255, cv2.THRESH_BINARY )
        #cropped = cv2.GaussianBlur(cropped, (21,21), 0 )
        cv2.imshow(c.N, c.crop)

    if False:
        #print( "({0:.2f},{1:.1f},{2:.2f},{3:.1f}{4:.0f})".format(
        print( "({0:.2f},{2:.2f},{4:.0f})".format(
            crops[0].crop.mean(), crops[0].crop.sum(),
            crops[1].crop.mean(), crops[1].crop.sum(), pos ))
    if not capturing:
        for c in crops:
            if c.crop.mean() > 4:
                capturing=True
                startTime = pos;
                break
    else:
        stop_capturing = True
        for c in crops:
            if c.crop.mean() > 4:
                stop_capturing = False
                break
        if stop_capturing:
            capturing = False
            cutlist.append((startTime, pos))
                

    #Show the full image scaled down. 
    thumb = cv2.resize(frame, (0,0), fx=0.4, fy=0.4 )
    if capturing:
        cv2.putText(thumb,"Recording {0:.0f}".format(pos/1000), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0))
    #else:
    #    cv2.putText(thumb,"None {0:.0f}".format(pos/1000), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))
        
    cv2.imshow('thumb',thumb)
    #print( frame.shape )
    k = cv2.waitKey(1) & 0xff
    if k == ord('q'):
        break

#clean up the cutlist by combining cuts that are close to each other.
last = None
new_cutlist = []
for i in cutlist:
    if not new_cutlist:
        new_cutlist.append( i )
    else:
        if pos - i[0] < 1000*2:
            new_cutlist[-1] = (new_cutlist[-1][0], i[1])
        else:
            new_cutlist.append(i)

#Only keep cuts that are at least 5 seconds long.
cutlist = [ x for x in cutlist if x[1]-x[0] > 1000*5 ]

#Print the list.
for i in cutlist:
    print( "segment ({0:.0f},{1:.0f} )".format(i[0]/1000, i[1]/1000) )



cap.release()
cv2.destroyAllWindows()
