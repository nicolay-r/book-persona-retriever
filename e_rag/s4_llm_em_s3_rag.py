import argparse
import json
from os.path import join

import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from utils import CACHE_DIR, CsvService
from utils_ceb import CEBApi
from utils_em import EMApi



def iter_passages_kb(kb, req_cat, req_v):
    for char_id, data in kb.items():
        for cat_name, emb_list in data.items():
            if cat_name != req_cat:
                continue
            # Plain content.
            for v, empathy_text in emb_list:
                cos_sim = np.dot(v, req_v) / (np.linalg.norm(v) * np.linalg.norm(req_v))
                yield cos_sim, [char_id, cat_name, empathy_text]


def iter_rag(d, handle_selected_names):

    for row in tqdm(d):
        em = EMApi.mistral_parse_em(row["response"])

        p_dict = {}

        # Assess the closest passages.
        for cat_name, empathy_texts in em.items():
            for empathy_text in empathy_texts:
                for similarity, data in iter_passages_kb(kb=kb, req_cat=cat_name, req_v=model.encode(empathy_text)):

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

        handle_selected_names(selected_names)

        # Format prompt for the original utterance.
        original_utterance = ''.join(row["prompt"].split(':')[1:])

        # Wrapping everything into a single prompt.
        prompt = [f"Given {EMApi.K} passages:"] + \
                 selected_passages + \
                 [f"Determine speaker \"X\" for text: {original_utterance}"] + \
                 ["From: {}".format(",".join(set(selected_names)))]

        yield row["id"], "\n".join(prompt)


parser = argparse.ArgumentParser(description="Composing Prompts with RAG technique")

parser.add_argument('--source', dest='src', type=str, default=join(EMApi.output_dir, u"./contexts_em.json"))
parser.add_argument('--output', dest='output', type=str, default=join(EMApi.output_dir, f"./{EMApi.book_id}_{EMApi.K}_rag.csv"))
parser.add_argument('--output-passages', dest='output_passages', type=str, default=join(EMApi.output_dir, f"./{EMApi.book_id}_{EMApi.K}_passages.txt"))

args = parser.parse_args()

ceb_api = CEBApi()
ceb_api.read_char_map()

# Using ChatGPT-4 inferred EM, compose embeddings.
kb = EMApi.embed_kb_em()

# Load source file.
d = None
with open(args.src, "r") as json_file:
    d = json.load(json_file)

# Save the result.
model = SentenceTransformer(EMApi.emb_model, cache_folder=CACHE_DIR)
names_from_passages = []
CsvService.write(target=args.output,
                 lines_it=iter_rag(d=d, handle_selected_names=lambda names: names_from_passages.append(names)),
                 header=["id", "text"])

# Save names from passages.
with open(args.output_passages, "w") as f:
    for line in names_from_passages:
        f.write(",".join(line) + "\n")
