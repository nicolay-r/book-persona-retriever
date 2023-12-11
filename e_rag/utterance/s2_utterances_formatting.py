from os.path import join
from utils import CsvService
from utils_ceb import CEBApi
from utils_em import EMApi


manual_chars = []
with open(join(EMApi.output_dir, f"./{EMApi.book_id}_mentions.txt"), 'r') as f:
    for line in f.readlines():
        l = line.strip()
        if len(l) < 1:
            continue
        manual_chars.append(l)

ceb_api = CEBApi()
ceb_api.read_char_map()

book_chars = manual_chars
for cid in ceb_api.iter_book_chars(EMApi.book_id):
    for char_name in ceb_api.get_char_names(cid):
        book_chars.append(char_name)


def it_lines():
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
                 lines_it=it_lines())