import json
from subprocess import call
import argparse
from os import path,getcwd

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
    for i in cutlist:
        #print ("cutting: {0}".format(i))
        cmd = ( "ffmpeg  -ss {2} -i {1} -t {3} -c:v copy -c:a copy {0:03d}_cut.mp4".format( count, i[0], (i[1]/1000), ((i[2]-i[1])/1000) ) )
        print( cmd )
        call(cmd)
        count += 1

if __name__ == '__main__':
    main()
