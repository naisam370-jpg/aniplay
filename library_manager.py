from history import load_history

def sort_series(series_list, mode="name"):
    history = load_history()

    if mode == "name":
        return sorted(series_list, key=lambda s: s["name"].lower())
    elif mode == "recent":
        return sorted(series_list, key=lambda s: history.get(s["name"], {}).get("position", 0), reverse=True)
    elif mode == "unwatched":
        return sorted(series_list, key=lambda s: history.get(s["name"], {}).get("completed", False))
    return series_list

def filter_series(series_list, mode="all"):
    history = load_history()

    if mode == "unwatched":
        return [s for s in series_list if not history.get(s["name"], {}).get("completed", False)]
    elif mode == "completed":
        return [s for s in series_list if history.get(s["name"], {}).get("completed", False)]
    return series_list
