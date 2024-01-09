from tqdm import tqdm

from core.database.sqlite3_api import SQLiteService
from core.utils import DictService, JsonService
from e_rag.utils_em import EMApi
from e_rag.utils_llm import iter_parse_mistral_parse_em
from utils import CsvService

# Read speaker names.
char_ids = [int(item[0].split("_")[1]) for item in
            CsvService.read(target=EMApi.mistral_7b_source, skip_header=True, cols=["speaker_id"])]

# Read Mistral responses.
speakers_em = {}
for row in tqdm(SQLiteService.iter_content(target=EMApi.mistral_7b_responses_sqlite, table="contents")):

    row_id = int(row[0])
    response = row[-1]
    char_ind = char_ids[row_id]

    if char_ind not in speakers_em:
        speakers_em[char_ind] = {}

    DictService.key_to_many_values(
        pairs_iter=iter_parse_mistral_parse_em(text=response, line_to_cat_func=EMApi.map_category),
        existed=speakers_em[char_ind])

for char_ind, em_data in tqdm(speakers_em.items(), desc="Saving"):
    if char_ind in EMApi.char_inds:
        JsonService.write(d=em_data, target=EMApi.kb_em_mistral_7b_v1_contexts(char_ind), silent=True)
