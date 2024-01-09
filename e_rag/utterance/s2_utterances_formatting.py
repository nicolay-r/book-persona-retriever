from os.path import join

from e_rag.utils_em import EMApi
from utils import CsvService


def iter_manual_chars():
    with open(join(EMApi.output_dir, f"./{EMApi.book_id}_mentions.txt"), 'r') as f:
        for line in f.readlines():
            l = line.strip()
            if len(l) < 1:
                continue
            yield l


def iter_lines(manual_chars):
    with open(join(EMApi.output_dir, f"./{EMApi.book_id}.txt"), "r") as f:
        yield "id", "text"
        for l in f.readlines():
            l = l.strip()
            meta, u = l.split(': ')
            u = u.replace('[USEP]', '')
            for c in manual_chars:
                u = u.replace(c, '[MASK]')
            yield meta, u


CsvService.write(target=join(EMApi.output_dir, f"./{EMApi.book_id}.csv"),
                 lines_it=iter_lines(manual_chars=list(iter_manual_chars())))