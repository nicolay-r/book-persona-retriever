from os.path import join, dirname, realpath
from gutenberg_dialog.pipeline.utils import DialogMetaHelper
from nltk import RegexpTokenizer

from core.book_dialog import BookDialogueService


class GuttenbergDialogApi:

    __current_dir = dirname(realpath(__file__))
    dialogs_en = join(__current_dir, "./data/filtered/en/dialogs_clean.txt")

    def iter_dialog_segments(self, book_path_func):
        assert(callable(book_path_func))

        bs = BookDialogueService()
        with open(self.dialogs_en, "r") as f:
            for l in f.readlines():
                if l.strip() == '~':
                    # break within a one dialog
                    pass
                elif l == '\n':
                    yield book_id, bs.annotate_dialog()
                elif l != '\n':
                    # actual utterance.
                    l = l.strip()

                    args = l.split(DialogMetaHelper._sep)
                    if len(args) == 1:
                        continue

                    meta, utt = args
                    book_id, dialog_region = meta.split('.txt')
                    bs.set_book(book_id=book_id, book_path=book_path_func(book_id))
                    # Span of paragraphs.
                    l_from, l_to = dialog_region[1:-1].split(":")
                    bs.set_paragraphs(l_from=l_from, l_to=l_to)
                    bs.register_utterance(utt=utt, l_from=l_from, l_to=l_to)

    def filter_utt_with_speaker_at_k(self, book_path_func, k=None):
        """ filter examples in distance from K
        """
        tokenizer = RegexpTokenizer(r'\w+')
        for book_id, lines in self.iter_dialog_segments(book_path_func):
            filtered = []
            for segment in lines:

                # Collect only author comments.
                if not (segment[0] in ['#', '.']):
                    continue

                # Crop meta-information.
                terms = segment.split()[1:]

                # Get rid o punctuation.
                tokenized_terms = tokenizer.tokenize(' '.join(terms))

                ######################################################
                # Check speaker at position K and no speakers behind.
                ######################################################
                is_ok = True
                is_char = lambda term: term.count('_') == 2
                if k is not None:
                    if k < len(tokenized_terms):
                        for i in range(k):
                            if is_char(tokenized_terms[i]):
                                is_ok = False
                                break
                        is_ok = is_ok and is_char(tokenized_terms[k])
                    else:
                        is_ok = False
                else:
                    is_ok = True
                ######################################################

                if not is_ok:
                    continue

                # Collect utterance.
                filtered.append(' '.join(tokenized_terms))

            if len(filtered) > 0:
                yield book_id, filtered
