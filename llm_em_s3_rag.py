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

        for row in tqdm(d):
            em = EMApi.mistral_parse_em(row["response"])

            p_list = []

            # Assess the closest passages.
            for cat_name, empathy_texts in em.items():
                for empathy_text in empathy_texts:
                    p_list += search_passage_kb(kb=kb, req_cat=cat_name, req_v=model.encode(empathy_text))

            # Order by cosine similarity.
            p_list = sorted(p_list, key=lambda item: item[0], reverse=True)

            # Keep top K passages.
            serialized_graph_passages = [
                "->".join([ceb_api.get_char_name(char_id=f"{EMApi.book_id}_{meta[0]}"), meta[1], meta[2]])
                for _, meta in p_list[:EMApi.K]]

            # Format prompt for the original utterance.
            original_utterance = ''.join(row["prompt"].split(':')[1:])

            # Wrapping everything into a single prompt.
            prompt = [f"Given {EMApi.K} passages:"] + \
                     serialized_graph_passages + \
                     [f"Select the speaker for text: {original_utterance}"] + \
                     ["Choices: {}".format(",".join([ceb_api.get_char_name(f"{EMApi.book_id}_{c}") for c in EMApi.chars]))]

            yield row["id"], "\n".join(prompt)


src = "data/llm_em/utternaces_em.json"
CsvService.write(target=f"data/llm_em/{EMApi.book_id}_rag.csv", lines_it=iter_rag(src))
