import argparse
from os.path import join

from core.book.paragraph import Paragraph
from core.book.utils import iter_paragraphs_with_n_speakers
from e_rag.utils_em import EMApi
from utils import CsvService
from utils_ceb import CEBApi
from utils_my import MyAPI


def iter_iterator_by_param(param_list, it_func):
    for p in param_list:
        for data in it_func(p):
            yield data


def handle_text(text):
    # TODO. This fix is expected to be adapted for the particular source type.
    # TODO. This is related to issue #43.
    text = text.replace("}", "} ").replace("{", " {")
    return " ".join(text.split())


def fix_paragraph_text(p):
    assert(isinstance(p, Paragraph))
    p.modify_text(handle_text)
    return p


def data_it():

    ceb_api = CEBApi()
    ceb_api.read_char_map()

    paragraphs_it = lambda n_speakers: iter_paragraphs_with_n_speakers(
        speakers=set(EMApi.char_ids),
        n_speakers=n_speakers,
        iter_paragraphs=map(lambda t: fix_paragraph_text(t),
                            CEBApi.iter_paragraphs(
                                iter_book_ids=[EMApi.book_id],
                                book_by_id_func=my_api.get_book_path)),
        multi_mentions=True)

    for paragraph, speakers in iter_iterator_by_param(param_list=args.speakers, it_func=paragraphs_it):
        assert(isinstance(paragraph, Paragraph))

        # Filter paragraph by length.
        if not(args.max_length > len(paragraph.Text) > args.min_length):
            continue

        yield ",".join(speakers), paragraph.Text


parser = argparse.ArgumentParser(
    description="Context Extraction from the dialogues of the literature novel books.")
parser.add_argument('--max', dest='max_length', type=int, default=200)
parser.add_argument('--min', dest='min_length', type=int, default=100)
parser.add_argument('--speakers', dest='speakers', type=int, default=[1, 2, 3])
args = parser.parse_args()

my_api = MyAPI()

CsvService.write(target=join(EMApi.output_dir, "paragraphs.csv"),
                 header=["speaker_id", "paragraph"],
                 lines_it=data_it())
