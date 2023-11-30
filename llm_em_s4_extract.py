from collections import Counter

from utils import CsvService
from utils_ceb import CEBApi
from utils_em import EMApi

ceb_api = CEBApi()
ceb_api.read_char_map()

etalon = []
for rid, line in enumerate(CsvService.read(target=f"data/llm_em/1184.csv", delimiter='\t', skip_header=True)):
    etalon.append(ceb_api.get_char_name(line[0]))

character_names = [ceb_api.get_char_name(f"{EMApi.book_id}_{c}") for c in EMApi.chars]

answers = []
counter = Counter()
for line in CsvService.read(target=f"data/llm_em/results.csv", delimiter=',', skip_header=True):
    _, _, response = line
    response = response.strip()
    found = []
    for char_name in character_names:
        if char_name in response:
            found.append(char_name)

    answers.append(found[0] if len(found) == 1 else "-")

    counter["defined"] += (len(found) == 1)
    counter["undefined"] += (len(found) != 1)
    counter["total"] += 1

assert(len(etalon) == len(answers))
print(len(etalon), len(answers))

for i in range(len(etalon)):
    counter["matched"] += etalon[i] == answers[i]

print(counter)
print("Defined", round(counter["defined"] / counter["total"], 2))
print("------")
print("Hits@1-defined", round(counter["matched"] / counter["defined"], 2))
print("Hits@1-total", round(counter["matched"] / counter["total"], 2))
