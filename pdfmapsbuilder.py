__author__ = 'remi'

import os
import sys
import time

from PIL import Image
Image.MAX_IMAGE_PIXELS = None


#def render():


if __name__ == '__main__':

    # Check if data sources volume is mounted
    volume = '/media/remi/DATA'
    scan_25 = '{0}/IGN/scan25.vrt'.format(volume)
    scan_100 = '{0}/IGN/scan100.vrt'.format(volume)

    if os.path.ismount(volume):
        if os.path.exists(scan_25) and os.path.exists(scan_100):
            params = sys.argv
            if len(params) == 6:

                print('\nXMIN:  {0}\nYMIN:  {1}\nXMAX:  {2}\nYMAX:  {3}\n\nTitle: {4}\n'
                      .format(params[1], params[2], params[3], params[4], params[5]))

                cwd = os.path.dirname(os.path.realpath(__file__))
                tmp_dir = '{0}/temp_{1}'.format(cwd, time.time())
                map_dir = '{0}/{1}'.format(tmp_dir, params[5])
                os.mkdir(tmp_dir)
                os.mkdir(map_dir)
            else:
                sys.exit('Error: Need at least 5 parameters\n'
                         'pdfmapsbuilder.py XMIN(int) YMIN(int) XMAX(int) YMAX(int) Title(str) Upload(bool)')
        else:
            sys.exit('Error: Raster sources doesn\'t exists')
    else:
        sys.exit('Error: DATA volume is not mounted')
