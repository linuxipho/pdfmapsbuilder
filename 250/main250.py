#!/usr/bin/python3

import os
import sys
import zipfile

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def tiler(src, j, i, l, a, b, xend, yend):
    extend = (j, i, j + xend, i + yend)
    tile = src.crop(extend)
    tile.save('{0}/tiles/{1}x{2}x{3}.png'.format(mappath, l, a, b), options='optimize')


def level_renderer(level, scale, resampling, source):
    """
    :param level: pdfmaps level
    :param scale: real scale
    :param resampling: pixel resampling methode
    :param source: current dataset source
    :return:
    """
    print('\nExtracting level {0} @ 1:{1}.000 scale...'.format(level, scale))
    extraction = 'gdalwarp -of GTiff -co COMPRESS=LZW -co BIGTIFF=YES -te {0} {1} {2} {3} -tr {4} {4} -r {5} -multi -wm 2048 {6} temp/out{7}.tif'.format(
        xmin, ymin, xmax, ymax, scale / 10.0, resampling, source, scale)
    os.system(extraction)
    print('OK')

    print('\nConversion au format PNG...')
    conversion = 'gdal_translate -of PNG -co ZLEVEL=1 temp/out{0}.tif temp/out{0}.png'.format(scale)
    os.system(conversion)
    print('OK')

    print('\nSuppression des fichiers annexes...')
    os.remove('temp/out{}.tif'.format(scale))
    os.remove('temp/out{}.png.aux.xml'.format(scale))
    print('OK')

    print('\nCréation des tuiles...')
    raster = Image.open('temp/out{}.png'.format(scale))

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
    print('OK')


def georeferencer():
    print('\nEcriture du fichier de géoréférencement...')
    proj = 'PROJCS["RGF93 / Lambert-93",GEOGCS["RGF93",DATUM["Reseau_Geodesique_Francais_1993",SPHEROID["GRS 1980",6378137,298.2572221010002,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6171"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4171"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["standard_parallel_1",49],PARAMETER["standard_parallel_2",44],PARAMETER["latitude_of_origin",46.5],PARAMETER["central_meridian",3],PARAMETER["false_easting",700000],PARAMETER["false_northing",6600000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","2154"]]'
    width = (xmax - xmin) / 5
    height = (ymax - ymin) / 5
    xOrigin = xmin + 2.5
    yOrigin = ymax - 2.5

    content = '{0}\n{1},5.0,0,{2},0,-5.0\n{3},{4}'.format(proj, xOrigin, yOrigin, width, height)

    ref = open('{0}/{1}.tif.ref'.format(mappath, mapname), 'wb')  # wb force strict \n
    ref.write(bytes(content, 'UTF-8'))
    ref.close()
    print('OK')


def thumbler():
    print('\nCréation de la miniature...')
    os.chdir(mappath)

    img = Image.open('tiles/2x2x2.png')
    extent = (0, 0, 64, 64)
    thumb = img.crop(extent)
    thumb.save('thumb.png')
    print('OK')


def packager():
    print('\nCompression...')
    os.chdir(mappath)
    archive_name = '../{0}.zip'.format(mapname)

    archive = zipfile.ZipFile(archive_name, mode="w", allowZip64=True)

    for dirname, subdirs, files in os.walk("."):
        for filename in files:
            archive.write(os.path.join(dirname, filename), os.path.join(dirname, filename), zipfile.ZIP_DEFLATED)

    archive.close()
    os.chdir(path)
    print('OK')


def cleaner():
    print('\nNettoyage')
    os.system('rm out*.png')
    os.system('rm -R temp/{0}'.format(mapname))
    print('OK')


if __name__ == '__main__':

    # General configuration
    path = os.path.dirname(os.path.realpath(__file__))
    volume = "/media/DATA"
    vrt_2 = "{0}/SIG/IGN/2015/SCEXP250/scexp250.vrt".format(volume)
    vrt_0 = "{0}/SIG/IGN/2015/SCEXP250/scexp1000.vrt".format(volume)

    # Run specific configuration
    mapname = 'france_250'
    xmin = 40000
    ymin = 6000000
    xmax = 1340000
    ymax = 7150000

    try:
        mappath = '{0}/temp/{1}'.format(path, mapname)
        os.mkdir(mappath)
        os.mkdir('{0}/tiles'.format(mappath))

        level_renderer(2, 250, 'near', vrt_2)
        level_renderer(1, 500, 'lanczos', vrt_2)
        level_renderer(0, 1000, 'lanczos', vrt_0)

        georeferencer()
        thumbler()
        packager()
        # cleaner()

    except KeyboardInterrupt:
        sys.exit(1)

    print('\nC\'est fini !\n\n\n')

