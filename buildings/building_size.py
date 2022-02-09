from os import environ

import geopandas as gpd
import matplotlib.pyplot as plt
from osdatahub import Extent, FeaturesAPI
from shapely.affinity import translate

# Get OS Data Hub API key
key = environ.get("OS_API_KEY")

# Define extent
extent = Extent.from_ons_code("E09000001")

# Define product
product = "zoomstack_local_buildings"

# Query Features API
features_api = FeaturesAPI(key, product, extent)
local_buildings = features_api.query(limit=1000000)

# Convert to GeoDataFrame
local_buildings_gdf = gpd.GeoDataFrame.from_features(
    local_buildings['features'], crs=extent.crs)
local_buildings_gdf.to_crs("EPSG:27700", inplace=True)

# Sort buildings by their footprint area
local_buildings_gdf.sort_values("SHAPE_Area", inplace=True)

# Move buildings according to their area
WIDTH = 2405
SPACE = 5

polygons = []
shift_x, shift_y = 0, 0
range_y, range_x = 0, 0
for building in local_buildings_gdf.itertuples():

    # Extract geometry and bounding box
    geometry = building.geometry
    min_x, min_y, max_x, max_y = geometry.bounds
    range_x = max_x - min_x

    # Check whether to wrap to next line
    if shift_x + range_x > WIDTH:
        shift_y += range_y + SPACE
        shift_x, range_y = 0, 0

    # Translate geometry
    shifted_geometry = translate(geometry,
                                 xoff=shift_x - min_x,
                                 yoff=shift_y - min_y)

    # Update polygons list
    polygons.append(shifted_geometry)

    # Update shift parameters
    range_y = max(max_y - min_y, range_y)
    shift_x += max_x - min_x + SPACE

# Create GeoSeries
gs = gpd.GeoSeries(polygons)

# Plot
EDGECOLOR = "#FFFFFF00"
FACECOLOR = "#FFFFFF"
BACKGROUND = "#222222"

fig, ax = plt.subplots(facecolor=BACKGROUND)
gs.plot(facecolor=FACECOLOR, edgecolor=EDGECOLOR, ax=ax)
plt.axis('off')
plt.show()
