#!/usr/bin/env python3
"""Fetch public data (no API key). Python standard library only."""
import json, datetime, urllib.request
def get(url, data=None, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "alberta-public-data-tracker"})
    if data is not None:
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "alberta-public-data-tracker", **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
import csv
URL = ("https://cwfis.cfs.nrcan.gc.ca/geoserver/public/ows?service=WFS&version=1.0.0&request=GetFeature"
       "&typeName=public:hotspots_last24hrs&outputFormat=application/json&CQL_FILTER=agency=%27AB%27")
d = get(URL)
pts = [{k: f["properties"].get(k) for k in ("lat","lon","rep_date","sensor","satellite","frp","fwi","hfi")} for f in d["features"]]
json.dump({"updated": NOW, "source": "CWFIS, Natural Resources Canada", "count": len(pts), "hotspots": pts}, open("data/latest.json","w"), indent=1)
with open("data/hotspots_last24h.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["lat","lon","rep_date","sensor","satellite","frp","fwi","hfi"]); w.writeheader(); w.writerows(pts)
print(f"alberta_hotspots_24h={len(pts)}")
