import rasterio
import numpy
from xml.dom import minidom

image_file = "20180202_074938_1008_3B_AnalyticMS1.tif" # Change here
metadata_file = "20180202_074938_1008_3B_AnalyticMS_metadata.xml"

# Load red and NIR bands - note all PlanetScope 4-band images have band order BGRN
with rasterio.open(image_file) as src:
    band_red = src.read(3)

with rasterio.open(image_file) as src:
    band_nir = src.read(4)

xmldoc = minidom.parse(metadata_file)
nodes = xmldoc.getElementsByTagName("ps:bandSpecificMetadata")

# XML parser refers to bands by numbers 1-4
coeffs = {}
for node in nodes:
    bn = node.getElementsByTagName("ps:bandNumber")[0].firstChild.data
    if bn in ['1', '2', '3', '4']:
        i = int(bn)
        value = node.getElementsByTagName("ps:reflectanceCoefficient")[0].firstChild.data
        coeffs[i] = float(value)

# Multiply by corresponding reflectance coefficients
band_red = band_red * coeffs[3]   # Change these two values
band_nir = band_nir * coeffs[4]

# Allow division by zero
numpy.seterr(divide='ignore', invalid='ignore')

# Calculate NDVI
ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)

# Set spatial characteristics of the output object to mirror the input
kwargs = src.meta
kwargs.update(
    dtype=rasterio.float32,
    count = 1)

# Create the file
with rasterio.open('20180202_074938_1008_NVDI.tif', 'w', **kwargs) as dst:  # Change file name
        dst.write_band(1, ndvi.astype(rasterio.float32))


import matplotlib.pyplot as plt
plt.imsave("ndvi_cmap.png", ndvi, cmap=plt.cm.summer)  # Change file name