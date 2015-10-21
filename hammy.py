import argparse
from os import path,getcwd
import cv2 as cv
from VideoPlayer import VideoPlayer
from Scanner import Scanner
import json
from timeit import default_timer as timer

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--left', required=False, default=path.join(getcwd(),'left.mp4'),
                        help='Left half of rink' )
    parser.add_argument('--left_regions', required=False)#, default=path.join(getcwd(),'left.mp4.json') )
    parser.add_argument('--right', required=False, default=path.join(getcwd(),'right.mp4'),
                        help='Right half of rink' )
    parser.add_argument('--right_regions', required=False)#, default=path.join(getcwd(),'right.mp4.json'))
    parser.add_argument('--debug', required=False, action='store_true',
                        help='Increase output level' )

    opts = parser.parse_args()
    return opts

def select_reference( file ):
    #with VideoPlayer(file) as vp:
        vp = VideoPlayer(file)
        vp.draw()
        
        while(True):
            k = cv.waitKey(1) & 0xff
            
            if k == ord('q'):
                retval = (vp.get_pos(), vp.get_regions())
                vp.release()
                break
            if k == ord('r'):
                vp.pop_region()
            if k == ord('n'):
                vp.step(1000)
                vp.draw()
            if k == ord('N'):
                vp.step(10000)
                vp.draw()
            if k == ord('p'):
                vp.step(-1000)
                vp.draw()
            if k == ord('P'):
                vp.step(-10000)
                vp.draw()
                
        return retval

class MovingAverageFilter:
	"""Simple moving average filter"""
 
	@property
	def avg(self):
		"""Returns current moving average value"""
		return self.__avg
 
	def __init__(self, n = 8, initial_value = 0):
		"""Inits filter with window size n and initial value"""
		self.__n = n
		self.__buffer = [initial_value/n]*n
		self.__avg = initial_value
		self.__p = 0
 
	def __call__(self, value):
		"""Consumes next input value"""
		self.__avg -= self.__buffer[self.__p]
		self.__buffer[self.__p] = value/self.__n
		self.__avg += self.__buffer[self.__p]
		self.__p = (self.__p  + 1) % self.__n
		return self.__avg
    
def main():
    opts = parse_args()

    print("left={0}".format(opts.left))
    print("right={0}".format(opts.right))

    if not opts.left_regions:
        l_pos, l_regions = select_reference( opts.left )
        with open( "{0}.json".format(opts.left), 'w') as f:
            json.dump( {'file':opts.left, 'pos':l_pos, 'regions':l_regions}, f )
    else:
        with open(opts.left_regions) as f:
            json_data = json.load(f)
            l_pos = json_data['pos']
            l_regions = json_data['regions']

    if not opts.right_regions:
        r_pos, r_regions = select_reference( opts.right )
        with open( "{0}.json".format(opts.right), 'w') as f:
            json.dump( {'file':opts.right, 'pos':r_pos, 'regions':r_regions}, f )
    else:
        with open(opts.right_regions) as f:
            json_data = json.load(f)
            r_pos = json_data['pos']
            r_regions = json_data['regions']

    l_scanner = Scanner(opts.left, l_pos, l_regions )
    r_scanner = Scanner(opts.right, r_pos, r_regions )

    l_avg = MovingAverageFilter(1, 0)
    r_avg = MovingAverageFilter(1, 0)

    #l_scanner.step(120*1000)
    #r_scanner.step(120*1000)
    
    start = timer()
    cutlist = []
    while True:
        l_score = l_avg(l_scanner.score())
        r_score = r_avg(r_scanner.score())
        pos = l_scanner.vp.get_pos()


        print( "scores:({2:.2f},{0:.2f},{1:.2f})".format(l_score, r_score, pos ) )

        if l_score > r_score:
            recording = opts.left
        else:
            recording = opts.right

        if not cutlist:
            cutlist = [(recording, pos, pos )]
        else:
            cutlist[-1] = cutlist[-1][:2] + (pos,)

            if recording != cutlist[-1][0]:
                cutlist.append((recording, pos,pos))

        #Step to the next frame.
        if (not l_scanner.step()) or (not r_scanner.step()):
            cutlist[-1] = cutlist[-1][:2] + (pos,)
            break
        
        #check to see if we have been told to quit. 
        k = cv.waitKey(1) & 0xff
        if k == ord('q'):
            print( "QUITING")
            l_scanner.release()
            r_scanner.release()
            break

    end = timer()
    print( 'elapsed time: {0}'.format(end-start) )
    
    #Now clean up the cutlist, merge any cuts shorter than the minimum seconds
    #with the cut before it. 
    new_cutlist = None
    for i in cutlist:
        if not new_cutlist:
            new_cutlist = [i]
        else:
            if i[0] == new_cutlist[-1][0]:
                new_cutlist[-1] = new_cutlist[-1][:2] + (i[2],)
            elif abs(i[2] - i[1]) < 1000*5:
                print("merging cut {0} with previous".format(i))
                new_cutlist[-1] = new_cutlist[-1][:2] + (i[2],)
            else:
                new_cutlist.append(i)

    cutlist = new_cutlist
    
    #print the list.
    for i in cutlist:
        print( "segment {0}".format(i) );

    with open(path.join(getcwd(),'cutlist.json'), 'w') as f:
        json.dump(cutlist, f)
        
    print('done')

if __name__ == '__main__':
    main()
