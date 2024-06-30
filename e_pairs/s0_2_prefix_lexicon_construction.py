from api.ldc import LdcAPI
from core.dialogue.comments_prefix import prefix_analysis, iter_lexicon_content, filter_non_addressed_cases


if __name__ == '__main__':

    ldc_api = LdcAPI()

    content_iter = iter_lexicon_content(
        speaker_positions=ldc_api.dialogs_recognize_speaker_at_positions,
        analysis_func=prefix_analysis,
        books_path_func=ldc_api.get_book_path,
        line_filter_func=filter_non_addressed_cases,
        p_threshold=ldc_api.dialogs_recongize_speaker_p_threshold,
        total=ldc_api.get_total_books())

    ldc_api.write_lexicon(rows_iter=content_iter)
