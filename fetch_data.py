#!/usr/bin/env python3
"""Fetch public data (no API key). Python standard library only."""
import json, datetime, urllib.request
import sys, time, socket, urllib.error

RETRY_DELAYS = (5, 15, 30)


def _retryable(err):
    if isinstance(err, urllib.error.HTTPError):
        return err.code == 429 or err.code >= 500
    return isinstance(err, (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError))


def urlopen_retry(req, timeout=60):
    """Open a URL, retrying temporary upstream errors. Exits cleanly if the source stays down."""
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception as err:
            if not _retryable(err):
                raise
            if attempt == len(RETRY_DELAYS):
                print(f"Source unavailable after {attempt + 1} attempts ({err}); keeping existing data.")
                sys.exit(0)
            print(f"Attempt {attempt + 1} failed ({err}); retrying in {RETRY_DELAYS[attempt]}s")
            time.sleep(RETRY_DELAYS[attempt])

def get(url, data=None, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "alberta-public-data-tracker"})
    if data is not None:
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "alberta-public-data-tracker", **(headers or {})})
    with urlopen_retry(req, timeout=60) as r:
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
