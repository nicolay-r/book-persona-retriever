from gutenberg_dialog.pipeline.utils import DialogMetaHelper

from api.gd import GuttenbergDialogApi
from api.ldc import LdcAPI
from core.book.book_dialog import BookDialogue


if __name__ == '__main__':

    # Initialize API.
    ldc_api = LdcAPI()
    books_dialogue = BookDialogue()
    gb_api = GuttenbergDialogApi()

    lines_to_consider = [
        BookDialogue.META_BEGIN_OF_DIALOG_LINE,
        BookDialogue.META_DIALOGUE_LINE,
        BookDialogue.META_AUTHOR_COMMENT_LINE,
        BookDialogue.META_END_OF_DIALOG_LINE
    ]

    with open(gb_api.dialogues_en, "r") as f:

        for line in f.readlines():

            if line.strip() == '~':
                # break within a one dialog
                pass

            elif line == '\n':
                annot = books_dialogue.annotate_dialog()
                print_sep = False
                for a in annot:
                    if a[0] in lines_to_consider:
                        print(book_id, a)
                        print_sep = True

                if print_sep:
                    print()

            elif line != '\n':
                # actual utterance.
                line = line.strip()

                args = line.split(DialogMetaHelper._sep)
                if len(args) == 1:
                    continue

                meta, utterance = args
                book_id, dialog_region = meta.split('.txt')
                books_dialogue.set_book(book_id=book_id, book_path=ldc_api.get_book_path(book_id))

                # Span of paragraphs.
                l_from, l_to = dialog_region[1:-1].split(":")
                books_dialogue.set_paragraphs(l_from=l_from, l_to=l_to)
                books_dialogue.register_utterance(utt=utterance, l_from=l_from, l_to=l_to)
