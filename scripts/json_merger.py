import json
import glob
import itertools


result = []
for f in glob.glob("./scrap_data/*.json"):
    with open(f, "rb") as infile:
        result.append(json.load(infile))
    print("[DONE]: ", f)

with open("merged_file.json", "w") as outfile:
    json.dump(
        list(itertools.chain.from_iterable(result)),
        outfile,
        indent=4,
        ensure_ascii=False,
    )
