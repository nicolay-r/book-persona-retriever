import json
from os.path import join

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

import utils
from core.utils import DictService
from utils import CACHE_DIR


class EMApi:
    """ Experiments with RAG.
    """
    K = 10
    book_id = 1184

    char_inds = [0, 3, 4, 5, 6, 7, 10, 12, 14, 17]
    char_ids = [f"1184_{i}" for i in char_inds]

    emb_model = 'all-mpnet-base-v2'
    categories = ['thinking and feeling', 'hearing', 'seeing', 'saying and doing', 'gains', 'pains']

    output_dir = join(utils.PROJECT_DIR, "./data/llm_em/")

    # Responses for EM extraction from different models.
    chatgpt4_1105_responses = lambda char_index: \
        join(EMApi.output_dir, f"./em-chatgpt4/{EMApi.book_id}_{char_index}.txt")
    mistral_7b_responses_sqlite = \
        join(output_dir, f"./dialogue-ctx-default.csv_mistralai_Mistral-7B-Instruct-v0.1.sqlite")
    mistral_7b_source = \
        join(output_dir, "dialogue-ctx-default.csv")

    # Mapping to the places they are formatted and stored.
    kb_em_chatgpt4_1106_summaries = lambda c: join(EMApi.output_dir, f"./kb/{EMApi.book_id}/em-chatgpt4-1106-summaries/{c}.json")
    kb_em_mistral_7b_v1_contexts = lambda c: join(EMApi.output_dir, f"./kb/{EMApi.book_id}/em-mistral-7b-v1-summaries/{c}.json")

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
    def iter_category_texts_from_json(json_src):
        with open(json_src, "r") as f:
            dict_data = json.load(f)
            for item in dict_data.items():
                yield item

    @staticmethod
    def embed_kb_em():
        """ Create embedding of the graph-alike representation of the character empathy mappings.
        """

        def iter_cat_data(cat_texts_iter):
            for cat, texts in cat_texts_iter:
                assert(isinstance(texts, list))
                cat = EMApi.map_category(cat)
                for text in texts:
                    assert(isinstance(text, str))
                    yield cat, (model.encode(text), text)

        # Sources for the KB.
        char_data_sources = [
            EMApi.kb_em_chatgpt4_1106_summaries,
            EMApi.kb_em_mistral_7b_v1_contexts
        ]

        model = SentenceTransformer(EMApi.emb_model, cache_folder=CACHE_DIR)
        embeddings = {}
        for char_ind in tqdm(EMApi.char_inds, desc="Embed characters EM"):
            for char_file_func in char_data_sources:
                cat_texts_iter = EMApi.iter_category_texts_from_json(char_file_func(char_ind))
                embeddings[char_ind] = DictService.key_to_many_values(pairs_iter=iter_cat_data(cat_texts_iter))

        return embeddings
