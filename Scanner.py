import cv2 as cv
from VideoPlayer import VideoPlayer

class Scanner:
    def __init__(self, path, ref_pos, regions, offset = 0):
        self.vp = VideoPlayer(path, False, gBlur = True)
        self.vp.seek(ref_pos)
        self.ref = self.vp.frame
        self.vp.seek(offset)
        self.regions = regions

    def release(self):
        self.vp.release()
        
    def step(self, msec=500):
        ret = self.vp.step(msec)
        if ret:
            self.vp.draw()
        return ret

    def score( self ):
        pixel_sum = 0
        pixel_count = 0
        for r in self.regions:
            ref_crop = self.ref[r[0][1]:r[1][1], r[0][0]:r[1][0]]
            ref_crop = cv.cvtColor(ref_crop, cv.COLOR_BGR2GRAY)
            crop = self.vp.frame[r[0][1]:r[1][1], r[0][0]:r[1][0]]
            crop = cv.cvtColor(crop, cv.COLOR_BGR2GRAY)
            crop = cv.absdiff(ref_crop, crop)
            #a, crop = cv.threshold(crop, 95, 255, cv.THRESH_BINARY)
            a, crop = cv.threshold(crop, 95, 1, cv.THRESH_BINARY)
            pixel_sum += crop.sum()
            pixel_count += crop.shape[0] * crop.shape[1]
            #print( "pixel_data:({0:.2f},{1:.2f}".format(pixel_sum, pixel_count))

        #First tried returning the average. 
        return (pixel_sum/pixel_count) * 100
        
        #Instead try returning the sum
        #return pixel_sum
