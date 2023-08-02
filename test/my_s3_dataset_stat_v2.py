from utils_my import MyAPI

speakers = []
with open("../data/ceb_books_annot/filtered_speakers.txt", "r") as f:
    for line in f.readlines():
        x = line.strip()
        speakers.append(x)

books = set()
for s in speakers:
    book_id = int(s.split('_')[0])
    books.add(book_id)

print("Speakers count (query and responses): {}".format(len(speakers)))
print("Books count: {}".format(len(books)))
print("Speakers per book: {}".format(round(len(speakers) / len(books), 2)))

c = 0
lines_iter = MyAPI.read_dataset(dataset_filepath=MyAPI.dataset_filepath, pbar=False)
dialogs_count = len(list(MyAPI.iter_dataset_as_dialogs(lines_iter)))
print("Dialogs count: {}".format(dialogs_count))
print("Dialogs per speaker: {}".format(round(dialogs_count/len(speakers), 2)))

for fold in ["train", "valid"]:
    lines_iter = MyAPI.read_dataset(dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=fold), pbar=False)
    dialogs_count = len(list(MyAPI.iter_dataset_as_dialogs(lines_iter)))
    print("Dialogs count [{}]: {}".format(fold, dialogs_count))


r_speaker_ids = set()
lines_iter = MyAPI.read_dataset(dataset_filepath=MyAPI.dataset_filepath, split_meta=True, pbar=False)
dialogs_iter = MyAPI.iter_dataset_as_dialogs(lines_iter)
for d in dialogs_iter:
    speaker_id = d[1][0]
    r_speaker_ids.add(speaker_id)
print("Speakers count (responses): {}".format(len(r_speaker_ids)))
