def format_ts_iso(ts: str) -> str:
    if not ts:
        return ""
    return ts.replace("T", " ")[:19]
