from os.path import realpath, dirname, join

from gutenberg_dialog.pipeline.utils import DialogMetaHelper

from core.book_dialog import BookDialogueService
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi

next_dialog = True
ceb_api = CEBApi()
bs = BookDialogueService()

# Make analysis of surrounded words based on TF-IDF for the case of
# char placed at first/second word

__current_dir = dirname(realpath(__file__))
total_m = 0
total_f = 0
with open(join(__current_dir, GuttenbergDialogApi.dialogs_en), "r") as f:

    for l in f.readlines():
        if l.strip() == '~':
            # break within a one dialog
            pass
        elif l == '\n':
            next_dialog = True
            annot = bs.annotate_dialog()
            for a in annot:
                pass
                if not (a[0] == '#'):
                    continue
                words = a.split()[1:]
                k = 1
                if not (k < len(words) and words[k][0] == '{'):
                    continue
                print(book_id, a)

            m, f = bs.stat()
            total_m += m
            total_f += f
        elif l != '\n':
            # actual utterance.
            l = l.strip()

            args = l.split(DialogMetaHelper._sep)
            if len(args) == 1:
                continue

            meta, utt = args
            book_id, dialog_region = meta.split('.txt')
            bs.set_book(book_id=book_id, ceb_api=ceb_api)
            # Span of paragraphs.
            l_from, l_to = dialog_region[1:-1].split(":")
            bs.set_paragraphs(l_from=l_from, l_to=l_to)
            bs.register_utterance(utt=utt, l_from=l_from, l_to=l_to)

print(total_m)
print(total_f)
