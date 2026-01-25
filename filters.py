def apply_filters(data, filters, stage_name=""):
    features = []
    for feature in data["features"]:
        remove = False
        reasons = []
        for flt in filters:
            should_remove, reason = flt(feature)
            if should_remove:
                remove = True
                if reason:
                    reasons.append(reason)
        if remove:
            name = feature.get("properties", {}).get("name", "unknown")
            print(f"[{stage_name}] Removed feature: name='{name}', reasons={reasons}")
            continue
        features.append(feature)
    data["features"] = features


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
    if (
        feature["geometry"]["type"] == "Point"
        and props.get("railway") in ("station", "halt")
        and props.get("city") is None
    ):
        return True, "city=None"
    return False, None


def pre_filter(data):
    features = []
    for feature in data["features"]:
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
        features.append(feature)
    data["features"] = features
    return data


def post_filter(data):
    features = []

    for feature in data["features"]:
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
        features.append(feature)
    data["features"] = features
    return data


FILTERS_PREFILTER = [
    filter_admin_centers,
    filter_tourism_usage,
]

FILTERS_POSTFILTER = [filter_no_city]
