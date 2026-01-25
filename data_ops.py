from shapely.geometry import shape

from colors import lighten_color
from config import *

def assign_city_to_points(features, city_polygons):
    for feature in features:
        if feature["geometry"]["type"] != "Point":
            continue

        feature_props = feature.setdefault("properties", {})
        point_geom = shape(feature["geometry"])
        feature_props["city"] = None

        for city_info in city_polygons:
            city_name = city_info["name"]
            city_polygon = city_info["polygon"]

            if city_polygon.contains(point_geom):
                feature_props["city"] = city_name
                feature_props["marker-color"] = CITIES.get(city_name, DEFAULT_COLOR)
                feature_props["marker-size"] = MARKER_SIZE
                feature_props["marker-symbol"] = MARKER_SYMBOL
                break


def build_city_polygons(features, city_colors):
    city_polygons = []

    for feature in features:
        geom_type = feature["geometry"]["type"]
        if geom_type not in ("Polygon", "MultiPolygon"):
            continue

        feature_props = feature.get("properties", {})
        city_name = feature_props.get("name")
        if city_name not in city_colors:
            continue

        city_polygon = shape(feature["geometry"])
        stroke_color = city_colors.get(city_name, DEFAULT_COLOR)
        fill_color = lighten_color(stroke_color, FILL_LIGHTEN_FACTOR)

        feature_props["stroke"] = stroke_color
        feature_props["stroke-width"] = STROKE_WIDTH
        feature_props["fill"] = fill_color

        city_polygons.append({
            "name": city_name,
            "polygon": city_polygon
        })

    return city_polygons
