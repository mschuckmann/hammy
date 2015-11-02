import json
from subprocess import call
import argparse
from os import path,getcwd

FILE=0
START=1
ACTIVE=2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cutlist', required=True, default=path.join(getcwd(),'cutlist.json'),
                        help='List of file cuts.' )
   
    opts = parser.parse_args()
    return opts

def main():
    opts = parse_args()

    print("cutlist={0}".format(opts.cutlist))

    cutlist = []
    with open( opts.cutlist ) as f:
        cutlist = json.load(f)

    count = 0
    cur_start = 0
    cur_active = True
    for i in cutlist:
        #print ("cutting: {0}".format(i))
        if cur_active:
            cmd = ( "ffmpeg  -i {1} -ss {2} -t {3} -c:v copy -c:a copy {0:03d}_cut.mp4".format( count, i[FILE], (cur_start/1000), ((i[START]-cur_start)/1000) ) )
            print( cmd )
            call(cmd)
            count += 1
            cur_start = i[START]
            cur_active = i[ACTIVE]

if __name__ == '__main__':
    main()
