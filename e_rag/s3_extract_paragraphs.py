import argparse
from os.path import join

from core.book.paragraph import Paragraph
from core.book.utils import iter_paragraphs_with_n_speakers
from core.service_csv import CsvService
from e_rag.utils_em import EMApi
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def iter_iterator_by_param(param_list, it_func):
    for p in param_list:
        for data in it_func(p):
            yield data


def data_it():

    ceb_api = CEBApi()
    ceb_api.read_char_map()

    p_it = lambda n_speakers: iter_paragraphs_with_n_speakers(
        speakers=set(EMApi.char_ids),
        n_speakers=n_speakers,
        iter_paragraphs=CEBApi.iter_paragraphs(
            iter_book_ids=[EMApi.book_id],
            book_by_id_func=my_api.get_book_path),
        paragraph_to_terms=lambda p: CEBApi.separate_character_entries(p.Text).split(),
        parse_speaker_or_none_func=lambda term:
            CEBApi.speaker_variant_to_speaker(
                GuttenbergDialogApi.try_parse_character(term, default=""),
                return_none=True),
        multi_mentions=True)

    for paragraph, speakers in iter_iterator_by_param(param_list=args.speakers, it_func=p_it):
        assert(isinstance(paragraph, Paragraph))

        # Filter paragraph by length.
        if not(args.max_length > len(paragraph.Text) > args.min_length):
            continue

        text = paragraph.Text
        if args.mask_speakers != "true":
            for speaker in speakers:
                char_id = ceb_api.speaker_variant_to_speaker(speaker_variant=speaker[1:-1])
                name = ceb_api.get_char_name(char_id=char_id)
                text = text.replace(speaker, name)

        yield ",".join(speakers), text


parser = argparse.ArgumentParser(
    description="Context Extraction from the dialogues of the literature novel books.")
parser.add_argument('--max', dest='max_length', type=int, default=200)
parser.add_argument('--min', dest='min_length', type=int, default=100)
parser.add_argument('--speakers', dest='speakers', type=int, default=[1, 2, 3])
parser.add_argument('--mask-speakers', dest='mask_speakers', type=str, default="false")
args = parser.parse_args()

my_api = MyAPI()

CsvService.write(target=join(EMApi.output_dir, "paragraphs.csv"),
                 header=["speaker_id", "paragraph"],
                 lines_it=data_it())
