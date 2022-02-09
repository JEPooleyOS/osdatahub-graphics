from os import environ

import geopandas as gpd
import matplotlib.pyplot as plt
from osdatahub import Extent, FeaturesAPI
from shapely.affinity import translate
from shapely.geometry import MultiLineString, LineString
from shapely.ops import linemerge

# Get OS Data Hub API key
key = environ.get("OS_API_KEY")

# Define extent
extent = Extent.from_ons_code("E09000001")

# Define product
product = "zoomstack_roads_local"

# Query Features API
features_api = FeaturesAPI(key, product, extent)
local_roads = features_api.query(limit=1000000)

# Convert to GeoDataFrame
local_roads_gdf = gpd.GeoDataFrame.from_features(
    local_roads['features'], crs=extent.crs)
local_roads_gdf.to_crs("EPSG:27700", inplace=True)

# Move buildings according to their area
def merge_lines(lines: list) -> LineString:
    """
    Turn a list of contiguous LineStrings into one LineString
    """
    multi_line = MultiLineString(lines)
    return linemerge(multi_line)

def stack_lines(lines: gpd.GeoDataFrame) -> LineString:
    """
    Transform all lines so that they are stacked end-to-end
    """
    stacked_lines = []
    end_x, end_y = 0, 0
    for line in lines.itertuples():
        
        # Extract geometry
        geometry = line.geometry
        
        # Transform lines to the end of the stack
        start_x, start_y = geometry.coords[0]
        shifted_line = translate(geometry,
                                     xoff=-start_x + end_x,
                                     yoff=-start_y + end_y)
        
        # Update shift parameters
        end_x, end_y = shifted_line.coords[-1]
        
        # Update stacked_lines list
        stacked_lines.append(shifted_line)

    return merge_lines(stacked_lines)

# Iterate the line stacking with a random order each time
paths = []
for _ in range(500):
    local_roads_gdf = local_roads_gdf.sample(frac=1)
    path = stack_lines(local_roads_gdf)
    paths.append(path)

# Create GeoSeries
gs = gpd.GeoSeries(paths)

# Plot
edgecolor = "#FFFFFF03"
background = "#222222"

fig, ax = plt.subplots(facecolor=background)
gs.plot(edgecolor=edgecolor, ax=ax)
plt.axis('off')
plt.show()
