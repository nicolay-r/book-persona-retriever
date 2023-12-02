import json

import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from utils import CACHE_DIR, CsvService
from utils_ceb import CEBApi
from utils_em import EMApi

# Using ChatGPT-4 inferred EM, compose embeddings.
kb = EMApi.embed_kb_em()


def search_passage_kb(kb, req_cat, req_v):
    r = []
    for char_id, data in kb.items():
        for cat_name, emb_list in data.items():
            if cat_name != req_cat:
                continue
            # Plain content.
            for v, empathy_text in emb_list:
                cos_sim = np.dot(v, req_v) / (np.linalg.norm(v) * np.linalg.norm(req_v))
                r.append((cos_sim, [char_id, cat_name, empathy_text]))
    return r

ceb_api = CEBApi()
ceb_api.read_char_map()

rag = []


def iter_rag(src):
    with open(src, "r") as f:
        d = json.load(f)
        model = SentenceTransformer(EMApi.emb_model, cache_folder=CACHE_DIR)

        yield "id", "text"

        names_list = []
        for row in tqdm(d):
            em = EMApi.mistral_parse_em(row["response"])

            p_dict = {}

            # Assess the closest passages.
            for cat_name, empathy_texts in em.items():
                for empathy_text in empathy_texts:
                    for item in search_passage_kb(kb=kb, req_cat=cat_name, req_v=model.encode(empathy_text)):
                        similarity, data = item

                        # Serialize the data.
                        passage = "->".join([ceb_api.get_char_name(char_id=f"{EMApi.book_id}_{data[0]}"),
                                             data[1], data[2]])

                        # Initialize the list for similarity values.
                        if passage not in p_dict:
                            p_dict[passage] = []

                        # Save the related similarity.
                        p_dict[passage].append(similarity)

            # Transform passages weights into averaged weights.
            p_list = [(passage, sum(similarities) / len(similarities)) for passage, similarities in p_dict.items()]

            # Order by similarity.
            p_list = sorted(p_list, key=lambda item: item[1], reverse=True)

            selected_passages = [meta for meta, _ in p_list[:EMApi.K]]
            selected_names = [passage.split('->')[0] for passage in selected_passages]
            names_list.append(selected_names)

            # Format prompt for the original utterance.
            original_utterance = ''.join(row["prompt"].split(':')[1:])

            # Wrapping everything into a single prompt.
            prompt = [f"Given {EMApi.K} passages:"] + \
                     selected_passages + \
                     [f"Select the one speaker for text: {original_utterance}"] + \
                     ["From: {}".format(",".join(set(selected_names)))]

            yield row["id"], "\n".join(prompt)

        with open("data/llm_em/passages_result.txt", "w") as f:
            for i in names_list:
                f.write(",".join(i) + "\n")


src = "data/llm_em/utternaces_em.json"
CsvService.write(target=f"data/llm_em/{EMApi.book_id}_{EMApi.K}_rag.csv", lines_it=iter_rag(src))
