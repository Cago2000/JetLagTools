from shapely.geometry import shape
from colors import *
from config import *
from filters import pre_filter, post_filter

data = pre_filter(data)

cities_polygons = []

for feature in data["features"]:
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

for feature in data["features"]:
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

data = post_filter(data)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print(f"\nGeoJSON saved: {OUTPUT_PATH}\n")

i = 1
for feature in data["features"]:
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
