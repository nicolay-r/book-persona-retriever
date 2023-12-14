from os.path import join

from utils import CsvService
from utils_em import EMApi


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
