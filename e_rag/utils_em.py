import json
from os.path import join

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import utils
from utils import CACHE_DIR


class EMApi:
    """ Experiments with RAG.
    """
    K = 10
    book_id = 1184
    char_ids = ["1184_0", "1184_3", "1184_4", "1184_5", "1184_6", "1184_7", "1184_10", "1184_12", "1184_14", "1184_17"]
    chars = [0, 3, 4, 5, 6, 7, 10, 12, 14, 17]
    emb_model = 'all-mpnet-base-v2'
    categories = ['thinking and feeling', 'hearing', 'seeing', 'saying and doing', 'gains', 'pains']
    output_dir = join(utils.PROJECT_DIR, "./data/llm_em/")

    @staticmethod
    def map_category(cat):
        if cat[-1] == ':':
            cat = cat[:-1]
        cat = cat.lower()
        if cat == 'doing' or cat == "saying":
            cat = "saying and doing"
        if cat == 'thinking' or cat == 'feeling':
            cat = "thinking and feeling"
        if cat not in EMApi.categories:
            return None
        return cat

    @staticmethod
    def embed_kb_em():
        """ Create embedding of the graph-alike representation of the character empathy mappings.
        """
        model = SentenceTransformer(EMApi.emb_model, cache_folder=CACHE_DIR)
        embeddings = {}
        for speaker_id in tqdm(EMApi.chars, desc="Embed characters EM"):

            json_src = join(EMApi.output_dir, f"./em-chatgpt4-fmt/{EMApi.book_id}_{speaker_id}.json")

            with open(json_src, "r") as f:
                emb_em = {}
                for cat, texts in json.load(f).items():
                    assert (isinstance(texts, list))
                    cat = EMApi.map_category(cat)
                    emb_em[cat] = []
                    for text in texts:
                        assert (isinstance(text, str))
                        emb_em[cat].append((model.encode(text), text))

                embeddings[speaker_id] = emb_em

        return embeddings

    @staticmethod
    def mistral_clear_em_instance(text):

        text = text.replace('</s>', '')

        if len(text) > 0 and text[0] in ["*", '+']:
            text = text[1:].strip()

        if len(text) > 0 and text[-1] == '.':
            text = text[:-1]

        if text.lower() in ["none", "none specified", "none mentioned"]:
            return None

        if "overall," in text.lower():
            return None

        return text

    @staticmethod
    def mistral_parse_em(text):
        em_dict = {}
        cat = None
        for line in text.split("\n"):
            l = line.strip()
            if len(l) < 1:
                continue
            if l[-1] == ':':
                cat = EMApi.map_category(l)
                if cat is None:
                    continue
                em_dict[cat] = []
                continue
            elif cat in em_dict:
                em_instance = EMApi.mistral_clear_em_instance(l)
                if em_instance is not None:
                    em_dict[cat].append(em_instance)
        return em_dict
