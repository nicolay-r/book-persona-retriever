from core.utils import JsonService, DictService
from e_rag.utils_em import EMApi
from e_rag.utils_llm import iter_parse_chatgpt4_1106_em


def iter_converted(src_func):
    for char_index in EMApi.char_inds:
        em_value_iter = iter_parse_chatgpt4_1106_em(src=src_func(char_index))
        yield char_index, DictService.key_to_many_values(pairs_iter=em_value_iter)


for c, d in iter_converted(src_func=EMApi.chatgpt4_1105_responses):
    JsonService.write(d=d, target=EMApi.kb_em_chatgpt4_1106_summaries(c))
