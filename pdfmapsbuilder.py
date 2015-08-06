__author__ = 'remi'

import os
import sys
import time
import shutil

from PIL import Image
Image.MAX_IMAGE_PIXELS = None


#def render():


if __name__ == '__main__':

    volume = '/media/remi/DATA'
    scan_25 = '{0}/IGN/scan25.vrt'.format(volume)
    scan_100 = '{0}/IGN/scan100.vrt'.format(volume)

    if os.path.ismount(volume) is False:
        sys.exit('Error: DATA volume is not mounted')

    if os.path.exists(scan_25) is False or os.path.exists(scan_100) is False:
        sys.exit('Error: At least on raster source path is invalid')

    params = sys.argv

    if len(params) < 6:
        sys.exit('Error: Need at least 5 parameters\n$> pdfmapsbuilder.py XMIN(int) YMIN(int) XMAX(int) YMAX(int) Title(str) Upload(bool)')

    cwd = os.path.dirname(os.path.realpath(__file__))
    tmp_dir = '{0}/temp_{1}'.format(cwd, time.time())
    map_dir = '{0}/{1}'.format(tmp_dir, params[5])

    try:
        os.mkdir(tmp_dir)
        os.mkdir(map_dir)




    finally:
        shutil.rmtree(tmp_dir)
        print('this is the end...')


