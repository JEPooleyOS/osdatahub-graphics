import geopandas as gpd
import matplotlib.pyplot as plt
from osdatahub import FeaturesAPI, Extent
from os import environ
from shapely.affinity import translate
from shapely.geometry import LineString


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

# "Polarise" the road network
def break_line(line: LineString) -> list:
    """
    Break LineString into its straight line segments
    """
    segment_coords = zip(line.coords[:-1], line.coords[1:])
    return list(map(LineString, segment_coords))


def polarise_lines(lines: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """
    Extract all straight line segments and transform them so that they emerge
    from a shared coordinate
    """
    segments = []
    for line in lines.itertuples():
        
        # Extract geometry
        geometry = line.geometry

        # Iterate through straight line segments
        for segment in break_line(geometry):
            
            # Transform lines to shared coordinate
            start_x, start_y = segment.coords[-1]
            shifted_segment = translate(segment,
                                        xoff=-start_x,
                                        yoff=-start_y)
            
            # Update segments list
            segments.append(shifted_segment)

    return gpd.GeoSeries(segments)

# Create polarised lines GeoSeries
polarised_roads = polarise_lines(local_roads_gdf)

# Plot
edgecolor = "#FFFFFF30"
background = "#222222"
linewidth = 2

fig, ax = plt.subplots(facecolor=background)
polarised_roads.plot(edgecolor=edgecolor, ax=ax, linewidth=linewidth)
plt.axis('off')
plt.show()