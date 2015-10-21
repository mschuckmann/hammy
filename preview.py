from __future__ import print_function
import argparse
from os import path,getcwd
import cv2 as cv
from VideoPlayer import VideoPlayer
from Scanner import Scanner
import json
from timeit import default_timer as timer
import sys


FILE=0
START=1
END=2

def LOG(txt):
    print( "LOG:{0}".format(txt), file=sys.stderr)
    sys.stderr.flush()
    

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cutlist', required=False, default=path.join(getcwd(),'cutlist.json'),
                        help='List of file cuts' )

    opts = parser.parse_args()
    return opts

class CutListPlayer:
    def __init__( cutlist ):
        self.cutlist = cutlist
        self.vps = {}
        self.cut = self.
        self.index = 0
        self.pos =
        
def adjust_start( cutlist, index, new_start ):
    if index < 0 or index >= len(cutlist):
        return
    LOG( "adjust_start:{0}={1},{2}".format(index, cutlist[index][START:], new_start) )
    if new_start == cutlist[index][START]:
        return
    if cutlist[index][END] - new_start >= 3000:
        cutlist[index][START]=new_start
        LOG( "[set start={0}={1}".format(index,cutlist[index][START:]))
        adjust_end( cutlist, index-1, new_start )
    else:
        adjust_start( custlist, index-1, cutlist[index][END] )
        remove_cut(cutlist, index)

def adjust_end( cutlist, index, new_end ):
    if index < 0 or index >= len(cutlist):
        return
    
    LOG( "adjust_end:{0}={1},{2}".format(index, cutlist[index][START:], new_end))
    if( new_end == cutlist[index][END] ):
        return
    if (new_end - cutlist[index][START]) >= 3000:
        cutlist[index][END]=new_end
        LOG( "[set end={0}={1}".format(index,cutlist[index][START:]))
        adjust_start( cutlist, index+1, new_end )
    else:
        adjust_start( custlist, index+1, cutlist[index][START] )
        remove_cut(cutlist, index)

def remove_cut( cutlist, index):
        LOG( "removing cut {0}={1}".format(index, cutlist[index][START:]))
#        prev_end = cutlist[index][2]
#        next_start = cutlist[index][1]
        del(cutlist[index])
#        adjust_end(cutlist, index-1, prev_end)
#        adjust_start(cutlist, index+1, next_start)
    

def main():
    opts = parse_args()

    LOG( "cutlist={0}".format(opts.cutlist))

    with open( opts.cutlist ) as f:
        cutlist = json.load(f)
        
    vps = {} 
    index = 0
    cut = cutlist[index]
    LOG( "[cut={0}={1}".format(index,cut[START:]))
    pos = cut[START]
    vps[cut[FILE]] = VideoPlayer( cut[FILE], False, "Video" )
    vps[cut[FILE]].seek(pos)
    vps[cut[FILE]].draw()
    running = False
   
    while True:
        if running:
            if vps[cut[FILE]].get_pos() >= cut[END]:
                if index < len(cutlist)-1:
                    index += 1
                    cut = cutlist[index]
                    LOG( "[cut={0}={1}".format(index,cut[START:]))
                    if not cut[FILE] in vps:
                        vps[cut[FILE]] = VideoPlayer( cut[FILE], False, "Video" )
                    pos = cut[START]
                    vps[cut[FILE]].seek(pos)
                    #vps[cut[FILE]].draw()
            #else:
            if not vps[cut[FILE]].next():
                running = False
            else:
                vps[cut[FILE]].draw()
                
        
        #check to see if we have been told to quit. 
        k = cv.waitKey(1) & 0xff
        if k == ord('q'):
            LOG( "QUITING")
            break
        elif k == ord('r'):
            running = not running
        elif k == ord('['):
            if index != 0:
                index -= 1
                cut = cutlist[index]
                LOG( "[cut={0}={1}".format(index,cut[START:]))
                if not cut[FILE] in vps:
                    vps[cut[FILE]] = VideoPlayer( cut[FILE], False, "Video" )
                pos = cut[START]
                vps[cut[FILE]].seek(pos)
                vps[cut[FILE]].draw()
        elif k == ord(']'):
            if index < len(cutlist)-1:
                index += 1
                cut = cutlist[index]
                LOG( "[cut={0}={1}".format(index,cut[START:]))
                if not cut[FILE] in vps:
                    vps[cut[FILE]] = VideoPlayer( cut[FILE], False, "Video" )
                pos = cut[START]
                vps[cut[FILE]].seek(pos)
                vps[cut[FILE]].draw()
        elif k == ord('n'):
            vps[cut[FILE]].step(100)
            vps[cut[FILE]].draw()
        elif k == ord('N'):
            vps[cut[FILE]].step(1000)
            vps[cut[FILE]].draw()
        elif k == ord('p'):
            vps[cut[FILE]].step(-100)
            vps[cut[FILE]].draw()
        elif k == ord('P'):
            vps[cut[FILE]].step(-1000)
            vps[cut[FILE]].draw()
        elif k == ord('s'):
            vps[cut[FILE]].seek(cut[1])
            vps[cut[FILE]].draw()
        elif k == ord('e'):
            vps[cut[FILE]].seek(cut[2])
            vps[cut[FILE]].draw()
        elif k == ord('S'):
            LOG("+SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
            adjust_start(cutlist, index, vps[cut[FILE]].get_pos() )
            LOG("-SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
        elif k == ord('E'):
            LOG("+EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
            adjust_end(cutlist, index, vps[cut[FILE]].get_pos() )
            LOG("-EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")

    for k in vps:
        vps[k].release()

    #with open(path.join(getcwd(),'cutlist.json'), 'w') as f:
    json.dump(cutlist, sys.stdout)

if __name__ == '__main__':
    main()
