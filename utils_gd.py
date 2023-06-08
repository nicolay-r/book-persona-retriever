from os.path import join, dirname, realpath
from gutenberg_dialog.pipeline.utils import DialogMetaHelper
from nltk import RegexpTokenizer

from core.book_dialog import BookDialogueService


class GuttenbergDialogApi:

    __tokenizer = RegexpTokenizer(r'\w+')
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

    def normalize_terms(self, terms):
        """ apply cleaning from punctuation signs.
        """
        assert(isinstance(terms, list))
        return self.__tokenizer.tokenize(' '.join(terms))

    @staticmethod
    def is_character(term):
        """ followed by CEB api.
        """
        if term.count('_') != 2:
            return False
        term = term.replace('_', '')
        if len(term) <= 2:
            return False
        if term[0] == '{' and term[-1] == '}':
            term = term[1:-1]
        return term.isnumeric()

    def filter_comment_with_speaker_at_k(self, book_path_func, k=None):
        """ filter examples in distance from K
        """
        for book_id, lines in self.iter_dialog_segments(book_path_func):
            filtered = []
            for segment in lines:

                # Collect only author comments.
                if not (segment[0] in ['#', '.']):
                    continue

                # Crop meta-information.
                terms = segment.split()[1:]

                # Get rid o punctuation.
                tokenized_terms = self.normalize_terms(terms)

                ######################################################
                # Check speaker at position K and no speakers behind.
                ######################################################
                is_ok = True
                if k is not None:
                    if k < len(tokenized_terms):
                        for i in range(k):
                            if self.is_character(tokenized_terms[i]):
                                is_ok = False
                                break
                        is_ok = is_ok and self.is_character(tokenized_terms[k])
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
