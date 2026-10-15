"""Apply the hand-written descriptions and drop the vendor copy."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CONTENT, write
from descriptions import DESCRIPTIONS

d = json.load(open(os.path.join(CONTENT, "databases.json"), encoding="utf-8"))
n = 0
for x in d["items"]:
    desc = DESCRIPTIONS.get(x["title"])
    if desc:
        x["description"] = desc
        n += 1
    x.pop("vendor_description", None)
    x.pop("badges", None)
print("  described %d of %d" % (n, len(d["items"])))
d["descriptions"] = "written for LITSA; vendor copy discarded"
write("databases.json", d)
