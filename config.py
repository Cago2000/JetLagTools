import json

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

with open(INPUT_PATH, encoding="utf-8") as f:
    data = json.load(f)
