import json
from shapely.geometry import shape

# ------------------------------
# Load configuration
# ------------------------------
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

INPUT_PATH = config.get("input_geojson", "map.geojson")
OUTPUT_PATH = config.get("output_geojson", "map_colored.geojson")
CITIES = config.get("cities", {})
FILL_LIGHTEN_FACTOR = config.get("fill_lighten_factor", 0.6)
STROKE_WIDTH = config.get("stroke_width", 2)
DEFAULT_COLOR = config.get("default_color", "#888888")
MARKER_SIZE = config.get("marker_size", "medium")
MARKER_SYMBOL = config.get("marker_symbol", "rail")

# ------------------------------
# Utility function to lighten a hex color
# ------------------------------
def lighten_color(hex_color, factor=0.5):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02X}{g:02X}{b:02X}"

# ------------------------------
# Load GeoJSON
# ------------------------------
with open(INPUT_PATH, encoding="utf-8") as f:
    geojson_data = json.load(f)

# ------------------------------
# Prepare city polygons for spatial checking
# ------------------------------
cities_polygons = []
for feature in geojson_data["features"]:
    geom_type = feature["geometry"]["type"]
    props = feature.get("properties", {})
    name = props.get("name", "unknown")
    
    if name not in CITIES:
        continue  # skip cities not in config
    
    if geom_type in ["Polygon", "MultiPolygon"]:
        polygon = shape(feature["geometry"])
        stroke_color = CITIES.get(name, DEFAULT_COLOR)
        fill_color = lighten_color(stroke_color, factor=FILL_LIGHTEN_FACTOR)
        feature.setdefault("properties", {})
        feature["properties"]["stroke"] = stroke_color
        feature["properties"]["stroke-width"] = STROKE_WIDTH
        feature["properties"]["fill"] = fill_color
        cities_polygons.append({"polygon": polygon, "name": name})

# ------------------------------
# Update station/point features with city colors
# ------------------------------
for feature in geojson_data["features"]:
    if feature["geometry"]["type"] != "Point":
        continue
    point = shape(feature["geometry"])
    for city in cities_polygons:
        if city["polygon"].contains(point):
            if "properties" not in feature:
                feature["properties"] = {}
            color = CITIES.get(city["name"], DEFAULT_COLOR)
            feature["properties"]["marker-color"] = color
            feature["properties"]["marker-size"] = MARKER_SIZE
            feature["properties"]["marker-symbol"] = MARKER_SYMBOL
            break  # stop at first containing city

# ------------------------------
# Save updated GeoJSON
# ------------------------------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, indent=2)

print(f"GeoJSON saved with colored city borders and stations: {OUTPUT_PATH}")
