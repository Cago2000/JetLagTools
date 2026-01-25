import json
from shapely.geometry import shape

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

def filter_admin_centers(feature):
    props = feature.get("properties", {})
    relations = props.get("@relations", [])
    roles = [r.get("role") for r in relations if "role" in r]
    if any(role == "admin_centre" for role in roles):
        return True, f"relation_roles={roles}"
    return False, None

def filter_tourism_usage(feature):
    usage = feature.get("properties", {}).get("usage")
    if usage == "tourism":
        return True, "usage=tourism"
    return False, None

def filter_no_city(feature):
    props = feature.get("properties", {})
    if feature["geometry"]["type"] == "Point" and props.get("railway") in ("station", "halt") and props.get("city") is None:
        return True, "city=None"
    return False, None

FILTERS_PREFILTER = [
    filter_admin_centers,
    filter_tourism_usage,
]

FILTERS_POSTFILTER = [
    filter_no_city
]

def lighten_color(hex_color, factor=0.5):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02X}{g:02X}{b:02X}"

with open(INPUT_PATH, encoding="utf-8") as f:
    geojson_data = json.load(f)

filtered_features = []

for feature in geojson_data["features"]:
    props = feature.get("properties", {})
    name = props.get("name", "unknown")
    remove = False
    reasons = []
    for flt in FILTERS_PREFILTER:
        should_remove, reason = flt(feature)
        if should_remove:
            remove = True
            if reason:
                reasons.append(reason)
    if remove:
        print(f"Removed feature: name='{name}', reasons={reasons}")
        continue
    filtered_features.append(feature)

geojson_data["features"] = filtered_features

cities_polygons = []

for feature in geojson_data["features"]:
    if feature["geometry"]["type"] not in ("Polygon", "MultiPolygon"):
        continue
    props = feature.get("properties", {})
    name = props.get("name")
    if name not in CITIES:
        continue
    polygon = shape(feature["geometry"])
    stroke_color = CITIES.get(name, DEFAULT_COLOR)
    fill_color = lighten_color(stroke_color, FILL_LIGHTEN_FACTOR)
    props["stroke"] = stroke_color
    props["stroke-width"] = STROKE_WIDTH
    props["fill"] = fill_color
    cities_polygons.append({"name": name, "polygon": polygon})

for feature in geojson_data["features"]:
    if feature["geometry"]["type"] != "Point":
        continue
    props = feature.setdefault("properties", {})
    point = shape(feature["geometry"])
    props["city"] = None
    for city in cities_polygons:
        if city["polygon"].contains(point):
            props["city"] = city["name"]
            props["marker-color"] = CITIES.get(city["name"], DEFAULT_COLOR)
            props["marker-size"] = MARKER_SIZE
            props["marker-symbol"] = MARKER_SYMBOL
            break

final_features = []

for feature in geojson_data["features"]:
    props = feature.get("properties", {})
    remove = False
    reasons = []
    for flt in FILTERS_POSTFILTER:
        should_remove, reason = flt(feature)
        if should_remove:
            remove = True
            if reason:
                reasons.append(reason)
    if remove:
        print(f"Removed feature: name='{props.get('name')}', reasons={reasons}")
        continue
    final_features.append(feature)

geojson_data["features"] = final_features

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, indent=2)

print(f"\nGeoJSON saved: {OUTPUT_PATH}")

i = 1
for feature in geojson_data["features"]:
    props = feature.get("properties", {})
    if feature["geometry"]["type"] == "Point" and props.get("railway") in ("station", "halt"):
        print(
            f"{i:03d} - {props.get('name')} | "
            f"city={props.get('city')} | "
            f"railway={props.get('railway')} | "
            f"category={props.get('railway:station_category')} | "
            f"usage={props.get('usage')} | "
            f"coords={feature['geometry']['coordinates']}"
        )
        i += 1
