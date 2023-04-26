import json

import pandas as pd
from tqdm import tqdm

personalities = pd.read_csv("data/fictional-character-personalities/personalities.txt", sep='\t')
print(len(personalities))
#print(personalities)
all_works = set(personalities["fictional_work"])
print(all_works)
print(len(all_works))
exit(0)

found = 0
ignored = 0
missed = 0
stat = {}
books = pd.read_csv("data/pg19/metadata.csv", header=None)
for t in tqdm(books[1][:2000]):
    args = [a.strip() for a in t.split('by')]
    if len(args) != 2:
        ignored += 1
        continue

    title, author = args
    ppp = personalities[personalities["fictional_work"].str.contains(title)]
    if len(ppp) == 0:
        missed += 1
        continue

    stat[t] = len(ppp)
    found += 1

print("found: {}".format(found))
print("ignored: {}".format(ignored))
print("missed: {}".format(missed))
print("----")
print("stat: {}".format(len(stat)))
with open("data/match_books_and_attributes.txt", "w") as f:
    json.dump(stat, f, indent=2)
