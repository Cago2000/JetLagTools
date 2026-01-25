import json
from data_io import load_data

config = load_data(input_path="config.json")

INPUT_PATH = config.get("input_geojson", "map.geojson")
OUTPUT_PATH = config.get("output_geojson", "map_colored.geojson")
CITIES = config.get("cities", {})
FILL_LIGHTEN_FACTOR = config.get("fill_lighten_factor", 0.6)
STROKE_WIDTH = config.get("stroke_width", 2)
DEFAULT_COLOR = config.get("default_color", "#888888")
MARKER_SIZE = config.get("marker_size", "medium")
MARKER_SYMBOL = config.get("marker_symbol", "rail")

data = load_data(input_path=INPUT_PATH)
