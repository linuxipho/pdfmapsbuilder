#!/usr/bin/python3

import os
import sys
import zipfile
# from multiprocessing import Process

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


class Builder:
    """
        The main class
    """

    def __init__(self, bbox, title):
        """
            Initialize the area variables
        """
        self.title = title
        self.xmin = bbox[0]
        self.ymin = bbox[1]
        self.xmax = bbox[2]
        self.ymax = bbox[3]
        os.mkdir('temp')
        os.mkdir('temp/{0}'.format(self.title))
        os.mkdir('temp/{0}/tiles'.format(self.title))

    def _tile(self, _src, _l, _i, _j, _iend, _jend, _aa, _bb):
        """
            Internal methode which create the requested tile
        """
        _extend = (_i, _j, _i + _iend, _j + _jend)
        _t = _src.crop(_extend)
        _t.save('temp/{}/tiles/{}x{}x{}.png'.format(self.title, _l, _aa, _bb), options='optimize')

    def run(self, _source, _level, _scale, _sample):
        """
            The main algorythme
        """

        # The extraction part
        _extract = 'gdalwarp -of PNG -te {0} {1} {2} {3} -tr {4} {4} -r {5} -multi -wm 2048 {6} temp/out{7}.tif'.format(
            self.xmin, self.ymin, self.xmax, self.ymax, _scale / 10.0, _sample, _source, _scale)
        os.system(_extract)

        # The rendering part
        _raster = Image.open('temp/out{}.png'.format(_scale))
        _wid, _hei = _raster.size
        _width = (_wid // 256) * 256
        _height = (_hei // 256) * 256
        _w = _wid % 256
        _h = _hei % 256

        _a = _b = _x = _y = 0

        for _y in range(0, _height, 256):
            for _x in range(0, _width, 256):
                self._tile(_raster, _level, _x, _y, _a, _b, 256, 256)
                _b += 1
            self._tile(_raster, _level, _x + 256, _y, _a, _b, _w, 256)
            _b = 0
            _a += 1

        for _x in range(0, _width, 256):
            self._tile(_raster, _level, _x, _y + 256, _a, _b, 256, _h)
            _b += 1
        self._tile(_raster, _level, _ + 256, _y + 256, _a, _b, _w, _h)


if __name__ == '__main__':

    # User defined variables
    mapname = 'test'
    bounds = (700000, 6500000, 750000, 6550000)

    # Advanced config
    path = os.path.dirname(os.path.realpath(__file__))
    volume = '/media/DATA'
    sc25 = '{0}/SIG/IGN/2014/sc25.vrt'.format(volume)
    sc100 = "{0}/SIG/IGN/2015/sc100.vrt".format(volume)
    levels = 3  # 2 or 3

    # Begin of the process
    try:

        pdfmap = Builder(bounds, mapname)
        pdfmap.run(sc25, 2, 25, 'near')
        pdfmap.run(sc25, 1, 25, 'lanczos')
        pdfmap.run(sc100, 0, 100, 'lanczos')

    except KeyboardInterrupt:
        sys.exit(1)