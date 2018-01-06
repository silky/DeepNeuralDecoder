#
# Author: Pooya Ronagh (2017)
# All rights reserved.
#
# This script takes input data from Christopher Chamberland's Matlab code
# and strips spaces, leaving the distance 3 surface code data in the format
# synX1synX2synX3 errX1errX2errX3 synZ1synZ2synZ3 errZ1errZ2errZ3
# for every iteration. 
# Ever line contains: 12bits + ' ' + 12bits + ' ' + 27bits + ' ' + 27bits
# If the entire matrix is all zeros, it is excluded.
# 

from __future__ import print_function, division
from builtins import range
import numpy as np
import sys
import os
import json

headers= [[1e-4, 1.885e-4, 4.3412e-6, 50758821], \
          [2e-4, 7.328e-4, 8.5572e-6, 25903477], \
          [3e-4, 0.0016, 1.2800e-5, 17599756], \
          [4e-4, 0.0028, 1.6763e-5, 13453791], \
          [5e-4, 0.0043, 2.0735e-5, 11005059], \
          [6e-4, 0.0062, 2.4745e-5, 9335235]]

def run(input_folder, output_folder, filename, header_line):

    print_epoch= 100000

    with open(input_folder + filename) as file:
        print(filename + ' ...')
        all_lines = file.readlines()

    print(len(all_lines)/3)
    outstream= open(output_folder + filename, 'w+')
    outstream.write(' '.join([str(elt) for elt in header_line]) + '\n')
    for line_num in range(len(all_lines)/3):
        if (not line_num % print_epoch):
            print(line_num)
        synx= []
        errx= []
        synz= []
        errz= []
        for i in range(3):
            xz_str=  ''.join(all_lines[3*line_num + i].split('\t')).strip()
            synx.append(xz_str[0:4])
            synz.append(xz_str[4:8])
            errx.append(xz_str[8:17])
            errz.append(xz_str[17:26])
        result= ' '.join(synx) + ' ' + ' '.join(errx) \
        + ' ' + ' '.join(synz) + ' ' + ' '.join(errz)
        if '1' in result:
            outstream.write(result + '\n')
        else:
            print('Warning at line ' + str(line_num))
            print(result)

    outstream.close()

if __name__ == '__main__':

    counter= 0
    for filename in os.listdir(sys.argv[1]):
        run(sys.argv[1], sys.argv[2], filename, headers[counter])
        sys.stdout.flush()
        counter+=1