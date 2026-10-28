from config import *
from data_io import dump_data
from filters import apply_filters, FILTERS_PREFILTER, FILTERS_POSTFILTER
from printing import print_valid_stations
from data_ops import assign_city_to_points, build_city_polygons, style_rail_lines, simplify_properties, keep_only_first_rail


def main():
    apply_filters(data, FILTERS_PREFILTER, stage_name="Pre-Filter")
    city_polygons = build_city_polygons(data["features"], CITIES)
    assign_city_to_points(data["features"], city_polygons)
    style_rail_lines(data["features"])
    apply_filters(data, FILTERS_POSTFILTER, stage_name="Post-Filter")
    simplify_properties(data["features"])
    data["features"] = keep_only_first_rail(data["features"])
    print_valid_stations(data["features"])
    dump_data(data=data, output_path=config["output_geojson"])


if __name__ == "__main__":
    main()