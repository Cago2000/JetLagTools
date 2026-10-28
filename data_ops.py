from shapely.geometry import shape

from colors import lighten_color
from config import *

RAIL_STROKE_COLOR = "#000000"
RAIL_STROKE_WIDTH = 1.5


def style_rail_lines(features):
    for feature in features:
        if feature["geometry"]["type"] not in ("LineString", "MultiLineString"):
            continue

        props = feature.get("properties", {})
        if props.get("railway"):
            feature_props = feature.setdefault("properties", {})
            feature_props["stroke"] = RAIL_STROKE_COLOR
            feature_props["stroke-width"] = RAIL_STROKE_WIDTH
            feature_props["color"] = RAIL_STROKE_COLOR
            feature_props["weight"] = RAIL_STROKE_WIDTH


def keep_only_first_rail(features):
    first_rail_found = False
    features_to_keep = []

    for feature in features:
        if feature["geometry"]["type"] in ("LineString", "MultiLineString"):
            if feature.get("properties", {}).get("railway") and not first_rail_found:
                first_rail_found = True
                features_to_keep.append(feature)
            elif feature.get("properties", {}).get("railway"):
                continue
            else:
                features_to_keep.append(feature)
        else:
            features_to_keep.append(feature)

    return features_to_keep


def sanitize_for_json(obj):
    if hasattr(obj, '__geo_interface__'):
        return obj.__geo_interface__
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    return obj


def simplify_properties(features):
    keep_by_type = {
        "Point": {"name", "marker-color", "marker-size", "marker-symbol", "city"},
        "LineString": {"stroke", "stroke-width"},
        "MultiLineString": {"stroke", "stroke-width"},
        "Polygon": {"name", "stroke", "stroke-width", "fill"},
        "MultiPolygon": {"name", "stroke", "stroke-width", "fill"},
    }

    for feature in features:
        geom_type = feature["geometry"]["type"]
        keep_keys = keep_by_type.get(geom_type, {"name"})

        props = feature.get("properties", {})
        keys_to_remove = [k for k in props.keys() if k not in keep_keys]
        for key in keys_to_remove:
            del props[key]

        feature["geometry"] = sanitize_for_json(feature["geometry"])
        feature["properties"] = sanitize_for_json(feature["properties"])


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

        city_polygons.append({"name": city_name, "polygon": city_polygon})

    return city_polygons