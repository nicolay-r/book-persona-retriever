from api.my import MyAPI


def calc_dataset_info(fold_index=None):
    """ Calculates stat for the particular fold of the dataset.
    """
    unique_books = set()
    unique_speakers = set()
    dialogs_count = 0

    filepath = MyAPI.dataset_fold_filepath.format(fold_index=fold_index) \
        if fold_index is not None else MyAPI.dataset_filepath

    line_it = MyAPI.read_dataset(dataset_filepath=filepath, keep_usep=True, split_meta=True, pbar=False)
    for dialog in MyAPI.iter_dataset_as_dialogs(dataset_lines_iter=line_it):
        assert(isinstance(dialog, list) and len(dialog) == 2)

        speaker_id = dialog[1][0]
        book_id = int(speaker_id.split('_')[0])

        unique_speakers.add(speaker_id)
        unique_books.add(book_id)
        dialogs_count += 1

    return len(unique_books), unique_speakers, dialogs_count


folding_names = [None] + \
                list(MyAPI.dataset_folding_fixed_parts.keys()) + \
                list(range(MyAPI.dataset_folding_parts))

speakers_by_fold = {}
print("----------------------------------------------------------------")
for fold_name in folding_names:
    books_count, r_speakers, dialogs_count = calc_dataset_info(fold_name)
    speakers_count = len(r_speakers)
    speakers_by_fold[fold_name] = r_speakers
    print("Folding name: {}".format(fold_name if fold_name is not None else "no-folding (all)"))
    print("Speakers count (query and responses): {}".format(speakers_count))
    print("Books count: {}".format(books_count))
    print("Speakers per book: {}".format(round(speakers_count / books_count, 2)))
    print("Dialogs count: {}".format(dialogs_count))
    print("Dialogs per speaker: {}".format(round(dialogs_count / speakers_count, 2)))
    print("Dialogs count [{}]: {}".format(str(fold_name), dialogs_count))
    print("----------------------------------------------------------------")


def check_intersection(foldings):
    assert(isinstance(foldings, list))
    for i in foldings:
        for j in foldings:
            if i == j:
                continue

            si = speakers_by_fold[i]
            sj = speakers_by_fold[j]
            assert (len(si.intersection(sj)) == 0)


# Check that we do not have intersections by speakers between folds.
check_intersection(list(MyAPI.dataset_folding_fixed_parts.keys()))
check_intersection(list(range(MyAPI.dataset_folding_parts)))
