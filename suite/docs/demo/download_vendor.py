#!/usr/bin/env python3
"""Fetch pinned, upstream browser dependencies into a documentation-only work directory."""
from pathlib import Path
import sys,urllib.request,concurrent.futures
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
packages={'chart.js':'chart.js@4.4.8/dist/chart.umd.js','chartjs-adapter-date-fns.js':'chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js','hammer.js':'hammerjs@2.0.8/hammer.min.js','chartjs-plugin-zoom.js':'chartjs-plugin-zoom@2.2.0/dist/chartjs-plugin-zoom.min.js','jsvectormap.js':'jsvectormap@1.6.0/dist/jsvectormap.min.js','world.js':'jsvectormap@1.6.0/dist/maps/world.js','jsvectormap.css':'jsvectormap@1.6.0/dist/jsvectormap.min.css'}
def fetch(item):
 name,url=item;data=urllib.request.urlopen('https://cdn.jsdelivr.net/npm/'+url,timeout=60).read();assert len(data)>1000;(out/name).write_bytes(data)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,packages.items()))
