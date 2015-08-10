__author__ = 'remi'

from osgeo import gdal
from gdalconst import *

print("Using GDAL %s" % gdal.__version__)

src_vrt = gdal.Open("/media/remi/Data/IGN/scan25.vrt", GA_ReadOnly)
driver = gdal.GetDriverByName("VRT")
tmp_vrt = driver.CreateCopy("", src_vrt, 0)


gdal.VSIFOpenL()


in_dataset = gdal.Open("/media/remi/Data/IGN/scan25.vrt", GA_ReadOnly)
driver = gdal.GetDriverByName("PNG")
out_dataset = driver.CreateCopy("out.png", in_dataset, 0, ['projwin 600000 6500000 650000 6450000'])

in_dataset = None
out_dataset = None
