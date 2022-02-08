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
product = "zoomstack_roads_local"

# Query Features API
features_api = FeaturesAPI(key, product, extent)
local_roads = features_api.query(limit=1000000)

# Convert to GeoDataFrame
local_roads_gdf = gpd.GeoDataFrame.from_features(
    local_roads['features'], crs=extent.crs)
local_roads_gdf.to_crs("EPSG:27700", inplace=True)

# Move buildings according to their area
x_shift, y_shift, y_range = 0, 0, 0
width = 2300
lines = []
end_x, end_y = 0, 0
for road in local_roads_gdf.itertuples():

    geometry = road.geometry
    start_x, start_y = geometry.coords[-1]
    shifted_geometry = translate(geometry,
                                 xoff=-start_x + end_x,
                                 yoff=-start_y + end_y)
    end_x, end_y = shifted_geometry.coords[-1]
    lines.append(shifted_geometry)

gs = gpd.GeoSeries(lines)

# Plot
edgecolor = "#FFFFFF20"
background = "#222222"

fig, ax = plt.subplots(facecolor=background)
gs.plot(edgecolor=edgecolor, ax=ax)
plt.axis('off')
plt.show()