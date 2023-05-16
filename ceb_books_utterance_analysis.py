from os.path import realpath, dirname, join

from utils_ceb import CEBApi


class BookService:

    def __init__(self):
        self.__book_id = None
        self.__book_text = None
        self.__lines = None
        self.__l_from = None
        self.__l_to = None
        self.__paragraph = None

    def set_book(self, book_id):
        # If already read this book and it is cached.
        if self.__book_id == book_id:
            return

        self.__book_id = book_id
        book_path = ceb_api.get_book_path(book_id)
        with open(book_path, "r") as b:
            text = b.read()

        self.__lines = text.split('\n')

    def find_paragraphs(self, l_from, l_to):

        # check if cached.
        if l_from is not None and \
                l_to is not None and \
                l_from == self.__l_from and \
                l_to == self.__l_to:
            return self.__paragraph

        self.__l_from = l_from
        self.__l_to = l_to
        self.__paragraph = ' '.join([l.strip() for l in self.__lines[int(l_from):int(l_to) + 5]])
        return self.__paragraph


__current_dir = dirname(realpath(__file__))
next_dialog = True
ceb_api = CEBApi()
bs = BookService()

dialogs_corrupted = 0
ok = 0
with open(join(__current_dir, "./data/filtered/en/dialogs.txt"), "r") as f:
    for l in f.readlines():
        if l.strip() == '~':
            # break within a one dialog
            pass
        elif l == '\n':
            next_dialog = True
        elif l != '\n':
            # actual utterance.
            l = l.strip()
            meta, utt = l.split('line:')
            book_id, dialog_region = meta.split('.txt')
            bs.set_book(book_id=book_id)
            # Span of paragraphs.
            l_from, l_to = dialog_region[1:-1].split(":")
            p_text = bs.find_paragraphs(l_from=l_from, l_to=l_to)
            utt_segments = [u.strip() for u in utt.split("[USEP]")]

            e_b_index = 0
            e_e_index = 0
            corrupted = False
            for i, utt_segment in enumerate(utt_segments):
                next_entry_index = p_text.index(utt_segment, e_b_index) if utt_segment in p_text else None

                print("[UTT]", utt_segment)

                if i > 0 and next_entry_index is not None:
                    print("[BREAK]", p_text[e_e_index+1:next_entry_index-1].strip())
                    pass

                if next_entry_index is None:
                    dialogs_corrupted += 1
                    corrupted = True
                    break
                else:
                    e_b_index = next_entry_index
                    e_e_index = e_b_index + len(utt_segment)
                    ok += 1

            # After dialog section extraction.
            if e_e_index is not None and not corrupted:
                try:
                    text_after = p_text[e_e_index + 1:p_text.index('.', e_e_index + 1)].strip()
                    print("[AFTER]", text_after.strip())
                except ValueError:
                    pass
                print("---")

print("-----------------")
print('ok: {}'.format(ok))
print('corrupted: {}'.format(dialogs_corrupted))
print("correct: {}\%".format(round(100*ok/(ok+dialogs_corrupted), 2)))
