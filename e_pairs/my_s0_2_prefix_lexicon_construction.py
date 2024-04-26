from tqdm import tqdm

from core.dialogue.comments_prefix import prefix_analysis, iter_lexicon_content, filter_non_addressed_cases
from utils_my import MyAPI


if __name__ == '__main__':

    my_api = MyAPI()

    content_iter = iter_lexicon_content(
        speaker_positions=my_api.dialogs_recognize_speaker_at_positions,
        analysis_func=prefix_analysis,
        books_path_func=my_api.get_book_path,
        line_filter_func=filter_non_addressed_cases,
        p_threshold=my_api.dialogs_recongize_speaker_p_threshold)

    my_api.write_lexicon(rows_iter=tqdm(content_iter))
