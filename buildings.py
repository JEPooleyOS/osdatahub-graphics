import geopandas as gpd
import matplotlib.pyplot as plt
from osdatahub import FeaturesAPI, Extent
from os import environ
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
x_shift, y_shift, y_range = 0, 0, 0
width = 2300
polygons = []
for building in local_buildings_gdf.itertuples():
    
    # Extract geometry and bounding box
    geometry = building.geometry
    min_x, min_y, max_x, max_y = geometry.bounds

    # Translate geometry
    shifted_geometry = translate(geometry,
                                 xoff=-min_x + x_shift,
                                 yoff=-min_y + y_shift)

    # Update polygons list
    polygons.append(shifted_geometry)
    
    # Update shift parameters
    y_range = max(max_y - min_y, y_range)
    x_shift += max_x - min_x + 5
    if x_shift > width:
        y_shift += y_range + 5
        x_shift, y_range = 0, 0

# Create GeoSeries
gs = gpd.GeoSeries(polygons)

# Plot
edgecolor = "#FFFFFF00"
facecolor = "#FFFFFF"
background = "#222222"

fig, ax = plt.subplots(facecolor=background)
gs.plot(facecolor=facecolor, edgecolor=edgecolor, ax=ax)
plt.axis('off')
plt.show()