import json

def dump_data(data, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\nGeoJSON saved: {output_path}\n")

def load_data(input_path: str, encoding="utf-8"):
    with open(input_path, encoding=encoding) as f:
        return json.load(f)