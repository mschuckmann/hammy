from __future__ import print_function
import argparse
from os import path,getcwd
import cv2 as cv
from VideoPlayer import VideoPlayer
from Scanner import Scanner
import json
from timeit import default_timer as timer
import sys
from datetime import timedelta
from Prune import prune


FILE=0
START=1
ACTIVE=2

def LOG(txt):
    print( "LOG:{0}".format(txt), file=sys.stderr)
    sys.stderr.flush()

def print_time(msec):
    if msec == -1:
        return str(msec)
    return str(timedelta(milliseconds=msec))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=False, default=path.join(getcwd(),'cutlist.json'),
                        help='List of file cuts' )
    parser.add_argument('--output', required=False, default='',
                        help='location to write the new cutlist')

    opts = parser.parse_args()
    return opts

class CutListPlayer:
    def __init__( self, cutlist ):
        self.cutlist = cutlist
        self.vps = {}
        self.idx = -1
        self.msec = 0
        self.next_frame()
        self.left = None
        self.right = None
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for k in self.vps:
            self.vps[k].release()
            
    def cut(self,idx=-1):
        if idx == -1:
            idx = self.idx

        if idx == len(self.cutlist):
            idx = -1
            
        return self.cutlist[idx]

    def start(self,idx=-1):
        if idx == -1:
            idx = self.idx

        if idx == len(self.cutlist):
            idx = -1

        return self.cutlist[idx][START]

    def end(self,idx=-1):
        if idx == -1:
            idx = self.idx
        if (idx + 1) < len(self.cutlist):
            return self.cutlist[idx+1][START]
        else:
            return -1

    def file(self,idx=-1):
        if idx == -1:
            idx = self.idx

        if idx == len(self.cutlist):
            idx = -1
            
        return self.cutlist[idx][FILE]
    
    def pos(self):
        return self.msec

    def index(self, msec=-1):
        if msec == -1:
            return self.idx
        
        for i in range(len(self.cutlist)):
            if msec >= self.start(i) and msec < self.end(i):
                return i
        return len(self.cutlist)

    def vp(self):
        if self.file() not in self.vps:
            self.vps[self.file()] = VideoPlayer(self.file(), False, "Cut Player")
        return self.vps[self.file()]
    
    def adjust_start( self, new_start, idx=-1 ):
        if idx == -1:
            idx = self.idx
        if idx > len(self.cutlist)-1 or new_start == self.start(idx):
            return
        LOG( "adjust_start:{0}={1},{2}".format(idx,self.cut(idx)[START:], print_time(new_start)) )
        if self.end(idx) == -1:
            self.cut(idx)[START] = new_start
        else:
            if (self.end(idx) - new_start) < 3000:
                self.cut(idx)[START] = self.end(idx)
            else:
                self.cut(idx)[START] = new_start

        self.cut(idx)[START]=new_start

    def adjust_end(self, new_end, idx=-1):
        if idx == -1:
            idx = self.idx

        if( idx > len(self.cutlist)-1 or new_end == self.end(idx) ):
            return
        LOG( "adjust_end:{0}={1},{2}".format(idx, self.cut(idx)[START:], print_time(new_end)))

        if self.end(idx) != -1:
            if (new_end - self.start(idx)) < 3000:
                self.cut(idx+1)[START] = self.start(idx)
            else:
                self.cut(idx+1)[START] = new_end
 
    def create_cut(self, pos):
        LOG("creating cut at ({0},{1})".format(self.idx, print_time(pos)))
        idx = self.idx
        self.cutlist.insert(idx+1, [self.file(), pos, True ] )
        self.seek(self.pos())
        
    def next_cut(self):
        if self.idx >= len(self.cutlist)-1:
            self.idx = len(self.cutlist)
        else:
            self.seek(self.start(self.idx+1))
            LOG("steping to next idx {0},{1}".format(self.idx, [self.file(),print_time(self.start()), self.cut()[ACTIVE]]))

    def previous_cut(self):
        if self.idx != 0:
            self.seek(self.start(self.idx-1))
            LOG("steping to previous idx {0},{1}".format(self.idx, [self.file(),print_time(self.start()), self.cut()[ACTIVE]]))
            
    def next_frame(self):
        #LOG ("next_frame: {0},{1}".format(print_time(self.vp().get_pos()), print_time(self.end())))
        if self.end() == -1 :
            frame = self.vp().next()
            self.msec = self.vp().get_pos()
            return frame

        if ((self.idx == -1) or (self.pos() >= self.end())):
            self.next_cut()
            return self.seek(self.pos())
        else:
            frame = self.vp().next()
            self.msec = self.vp().get_pos()
            return frame
   
    def draw(self):
        self.vp().set_text("{0},{1},{2}".format(self.idx,self.cut()[ACTIVE],len(self.cutlist)))
        self.vp().draw()

    def seek(self, msec ):
        self.msec = msec
        self.idx = self.index(msec)
        return self.vp().seek(self.pos())

    def step(self, msec ):
        return self.seek(self.pos()+msec)

    def set_left(self):
        if not self.left:
            self.left = self.file()
        else:
            self.cut()[FILE] = self.left

    def set_right(self):
        if not self.right:
            self.right = self.file()
        else:
            self.cut()[FILE] = self.right

    def toggle_active(self):
        self.cut()[ACTIVE] = not self.cut()[ACTIVE] 
            
def main():
    opts = parse_args()

    LOG( "cutlist={0}".format(opts.input))

    with open( opts.input ) as f:
        cutlist = json.load(f)

    with CutListPlayer(cutlist) as player:
        player.draw()
        running = 0
       
        while True:
            if running != 0:
                if running == 1:
                    frame = player.next_frame()
                else:
                    player.step(running)
                if frame:
                    player.draw()
                else:
                    running = 0

            #check to see if we have been told to quit. 
            k = cv.waitKey(1) & 0xff
            if k == ord('q'):
                LOG( "QUITING")
                break
            elif k == ord( ' ' ):
                running = 0
            elif k == ord('r'):
                if running == 0:
                    running = 1
                elif running == 1:
                    running = 500
                else: 
                    running += 500
            elif k == ord('['):
                player.previous_cut()
                LOG( "[cut={0}={1}".format(player.index(),print_time(player.cut()[START])))
                player.draw()
            elif k == ord(']'):
                player.next_cut()
                LOG( "[cut={0}={1}".format(player.index(),print_time(player.cut()[START])))
                player.draw()
            elif k == ord('n'):
                player.step(100)
                player.draw()
            elif k == ord('N'):
                player.step(1000)
                player.draw()
            elif k == ord('p'):
                player.step(-100)
                player.draw()
            elif k == ord('P'):
                player.step(-1000)
                player.draw()
            elif k == ord('2'):
                player.step(2000)
                player.draw()
            elif k == ord('5'):
                player.step(5000)
                player.draw()
            elif k == ord('9'):
                player.step(9000)
                player.draw()
            elif k == ord('s'):
                player.seek(player.start())
                player.draw()
            elif k == ord('e'):
                player.seek(player.end())            
                player.draw()
            elif k == ord('S'):
                LOG("+SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
                player.adjust_start(player.pos())
                LOG("-SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
            elif k == ord('E'):
                LOG("+EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
                player.adjust_end(player.pos())
                LOG("-EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            elif k == ord('c'):
                player.create_cut(player.pos())
                player.draw()
            elif k == ord('l'):
                player.set_left()
                player.draw()
            elif k == ord('k'):
                player.set_right()
                player.draw()
            elif k == ord('a'):
                player.toggle_active()
                player.draw()


    print("Merging neighboring cuts")

    cutlist = prune( cutlist )

    json.dump(cutlist, sys.stdout, indent=2, separators=(',',': '))

    if opts.output:
        with open(opts.output, 'w') as f:
            json.dump(cutlist, f)


if __name__ == '__main__':
    main()
