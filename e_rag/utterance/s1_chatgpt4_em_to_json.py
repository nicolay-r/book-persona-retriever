import json
from os.path import join

from utils_em import EMApi


for c in EMApi.chars:
    src = join(EMApi.output_dir, f"./em-chatgpt4/{EMApi.book_id}_{c}")
    d = {}
    cat = None
    with open(src + ".txt", "r") as f:
        for l in f.readlines():
            # Skipping comment.
            l = l.strip()
            if l[0] == '#':
                continue
            # Setup category.
            if l[-1] == ':':
                cat = l
                d[cat] = []
                continue
            else:
                d[cat].append(l)

    target = join(EMApi.output_dir, f"./em-chatgpt4-fmt/{EMApi.book_id}_{c}.json")
    with open(target, "w") as f:
        print(f"Save: {target}")
        json.dump(d, f, indent=4, ensure_ascii=False)
