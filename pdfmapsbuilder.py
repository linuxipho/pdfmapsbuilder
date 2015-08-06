__author__ = 'remi'

import os
import sys
import time
import shutil

from PIL import Image
Image.MAX_IMAGE_PIXELS = None


def tiler(src, j, i, l, a, b, xend, yend):
    extend = (j, i, j + xend, i + yend)
    tile = src.crop(extend)
    tile.save('{0}/tiles/{1}x{2}x{3}.png'.format(map_dir, l, a, b), options='optimize')


def level_renderer(level, scale, resampling, source):
    """
    :param level: pdfmaps level
    :param scale: real scale
    :param resampling: pixel resampling methode
    :param source: current dataset source
    """

    conversion = 'gdal_translate -of PNG -co ZLEVEL=1 -projwin {0} {3} {2} {1} -tr {4} {4} -r {5} {6} {7}/out{8}.png'\
        .format(xmin, ymin, xmax, ymax, scale / 10.0, resampling, source, tmp_dir, scale)
    os.system(conversion)

    raster = Image.open('{0}/out{1}.png'.format(tmp_dir, scale))

    WIDTH, HEIGHT = raster.size
    width = (WIDTH // 256) * 256
    height = (HEIGHT // 256) * 256
    W = WIDTH % 256
    H = HEIGHT % 256

    a = b = 0

    for y in range(0, height, 256):
        for x in range(0, width, 256):
            tiler(raster, x, y, level, a, b, 256, 256)
            b += 1
        tiler(raster, x + 256, y, level, a, b, W, 256)
        b = 0
        a += 1

    for x in range(0, width, 256):
        tiler(raster, x, y + 256, level, a, b, 256, H)
        b += 1
    tiler(raster, x + 256, y + 256, level, a, b, W, H)


def georeferencer():
    proj = 'PROJCS["RGF93 / Lambert-93",GEOGCS["RGF93",DATUM["Reseau_Geodesique_Francais_1993",SPHEROID["GRS 1980",6378137,298.2572221010002,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4171"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],PARAMETER["latitude_of_origin",46.5],PARAMETER["central_meridian",3],PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","2154"]]'
    width = (xmax - xmin) / 5
    height = (ymax - ymin) / 5
    xOrigin = xmin + 2.5
    yOrigin = ymax - 2.5

    content = '{0}\n{1},5.0,0,{2},0,-5.0\n{3},{4}'.format(proj, xOrigin, yOrigin, width, height)

    ref = open('{0}/{1}.tif.ref'.format(map_dir, mapname), 'wb')  # wb force strict \n
    ref.write(bytes(content, 'UTF-8'))
    ref.close()


def thumbler():
    img = Image.open('{0}/2x2x2.png'.format(tiles_dir))
    extent = (0, 0, 128, 128)
    thumb = img.crop(extent)
    thumb.save('{0}/thumb.png'.format(map_dir))


def packager():
    os.chdir(map_dir)
    archive_name = '../../{0}.zip'.format(mapname)

    archive = zipfile.ZipFile(archive_name, mode="w", allowZip64=True)

    for dirname, subdirs, files in os.walk("."):
        for filename in files:
            archive.write(os.path.join(dirname, filename), os.path.join(dirname, filename), zipfile.ZIP_DEFLATED)

    archive.close()


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

    xmin = params[1]
    ymin = params[2]
    xmax = params[3]
    ymax = params[4]
    mapname = params[5]

    cwd = os.path.dirname(os.path.realpath(__file__))
    tmp_dir = '{0}/temp_{1}'.format(cwd, time.time())
    map_dir = '{0}/{1}'.format(tmp_dir, params[5])
    tiles_dir = '{0}/tiles'.format(map_dir)

    try:
        os.mkdir(tmp_dir)
        os.mkdir(map_dir)
        os.mkdir(tiles_dir)

        level_renderer(2, 25, 'near', scan_25)
        level_renderer(1, 50, 'lanczos', scan_25)
        level_renderer(0, 100, 'lanczos', scan_100)

        georeferencer()
        thumbler()
        packager()


    finally:
        shutil.rmtree(tmp_dir)
        print('this is the end...')


