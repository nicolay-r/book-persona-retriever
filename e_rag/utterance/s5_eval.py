from collections import Counter
from os.path import join
from random import Random

from utils import CsvService
from utils_ceb import CEBApi
from utils_em import EMApi

ceb_api = CEBApi()
ceb_api.read_char_map()

etalon = []
for rid, line in enumerate(CsvService.read(target=join(EMApi.output_dir, f"./1184.csv"),
                                           delimiter='\t',
                                           skip_header=True)):

    etalon.append(ceb_api.get_char_name(line[0]))

character_names = [ceb_api.get_char_name(f"{EMApi.book_id}_{c}") for c in EMApi.chars]

answers = []
llm_counter = Counter()
for line in CsvService.read(target=join(EMApi.output_dir, f"./r_flant5_10.csv"),
                            delimiter='\t',
                            skip_header=True):
    _, _, response = line
    response = response.strip()
    found = []
    for char_name in character_names:
        if char_name in response:
            found.append(char_name)

    answers.append(found[0] if len(found) == 1 else "-")

    llm_counter["defined"] += (len(found) == 1)
    llm_counter["undefined"] += (len(found) != 1)
    llm_counter["total"] += 1

assert(len(etalon) == len(answers))

for i in range(len(etalon)):
    llm_counter["matched"] += etalon[i] == answers[i]

print("MISTRAL-7B Results")
print("------")
print("Defined", round(llm_counter["defined"] / llm_counter["total"], 2))
print("Hits@1-defined", round(llm_counter["matched"] / llm_counter["defined"], 2))
print("Hits@1-total", round(llm_counter["matched"] / llm_counter["total"], 2))
print(llm_counter)


baseline_counter = Counter()
all_answers = []
passages_answers = []

target = join(EMApi.output_dir, f"./{EMApi.book_id}_{EMApi.K}_passages.txt")
with open(target, "r") as f:
    for line in f.readlines():
        baseline_counter["total"] += 1
        line = line.strip()
        if len(line) == 0:
            all_answers.append([])
            passages_answers.append('-')
            baseline_counter["undefined"] += 1
            continue
        names = line.split(',')
        c = Counter()
        for n in names:
            c[n] += 1
        all_answers.append(list(c.keys()))
        passages_answers.append(c.most_common()[0][0])
        baseline_counter["defined"] += 1

random = Random()
assert(len(etalon) == len(passages_answers))
for i in range(len(etalon)):
    baseline_counter["matched"] += etalon[i] == passages_answers[i]
    baseline_counter["best"] += etalon[i] in all_answers[i]
    if len(all_answers[i]) > 0:
        baseline_counter["random"] += all_answers[i][random.randint(0, len(all_answers[i])-1)] == etalon[i]



print()
print("PASSAGES RESULTS")
print("------")
print("Defined", round(baseline_counter["defined"] / baseline_counter["total"], 2))
print("Hits@1-defined", round(baseline_counter["matched"] / baseline_counter["defined"], 2))
print("Hits@1-total", round(baseline_counter["matched"] / baseline_counter["total"], 2))
print("RANDOM", round(baseline_counter["random"] / baseline_counter["total"], 2))
print("Covered", round(baseline_counter["best"] / baseline_counter["total"], 2))
print(baseline_counter)


def it_analysis(prompt):
    yield ["id", "text"]
    for i, line in enumerate(CsvService.read(target=f"data/llm_em/r_flant5_10.csv", delimiter='\t', skip_header=True)):
        # Covered but not the same so we may form a prompt.
        if etalon[i] in all_answers[i] and etalon[i] != passages_answers[i]:
            r = line[1]
            r = r.replace("Select the one speaker ", "")
            line[1] = r.split("\nFrom: ")[0] + prompt.format(predict=answers[i], etalon=etalon[i])
            yield line[:-1]


prompts = {
    "explain_e_a": "\nExplain why the speaker is '{etalon}' but not `{predict}`?",
    "explain_e": "\nExplain why the correct speaker is '{etalon}'?",
    "explain_a": "\nExplain why answer is '{predict}'?",
}

for key, value in prompts.items():
    CsvService.write(target=join(EMApi.output_dir, f"./r_flant5_10_analysis-{key}.csv"),
                     lines_it=it_analysis(value))

