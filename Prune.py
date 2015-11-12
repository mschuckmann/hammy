import argparse
from os import path,getcwd
import json
import sys

FILE=0
START=1
ACTIVE=2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=False, default=path.join(getcwd(),'cutlist.json'),
                        help='List of file cuts' )
    parser.add_argument('--output', required=False, default='',
                        help='location to write the new cutlist')
    opts = parser.parse_args()
    return opts

    opts = parse_args()

def prune( cutlist ):
    new_cutlist = None
    for i in cutlist:
        if new_cutlist and new_cutlist[-1][START] > i[START]:
            print( "ERROR cuts out of order at {0} {1} {2}".format( len(new_cutlist), new_cutlist[-1][START], i[START]))
        if not new_cutlist:
            new_cutlist = [i]
        elif (abs(i[START] - new_cutlist[-1][START]) < 5000):
            if len(new_cutlist) > 1 and new_cutlist[-2][FILE] == i[FILE]:
                del(new_cutlist[-1])
            else:
                new_cutlist[-1] = i
        elif new_cutlist[-1][FILE] != i[FILE] or new_cutlist[-1][ACTIVE] != i[ACTIVE] and new_cutlist[-1][START] < i[START]:
            new_cutlist.append(i)
            
    return new_cutlist

    
def main():
    opts = parse_args()
    
    with open( opts.input ) as f:
        cutlist = json.load(f)
        
    cutlist = prune( cutlist )

    json.dump(cutlist, sys.stdout, indent=2, separators=(',',': '))

    if opts.output:
        with open(opts.output, 'w') as f:
            json.dump(cutlist, f)

            

if __name__ == '__main__':
    main()
