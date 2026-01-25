def print_valid_stations(features):
    i = 1
    for feature in features:
        props = feature.get("properties", {})
        if feature["geometry"]["type"] == "Point" and props.get("railway") in (
            "station",
            "halt",
        ):
            print(
                f"{i:03d} - {props.get('name')} | "
                f"city={props.get('city')} | "
                f"railway={props.get('railway')} | "
                f"category={props.get('railway:station_category')} | "
                f"coords={feature['geometry']['coordinates']}"
            )
            i += 1
