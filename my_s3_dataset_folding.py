from core.utils import chunk_into_n
from utils import cat_files
from utils_my import MyAPI


def write_folded_dataset(k, dialog_iter_func, speakers):
    """ Folding with the even splits of the utterances.
    """
    assert(isinstance(k, int))
    assert(isinstance(speakers, list))
    assert(callable(dialog_iter_func))

    speaker_ids_per_fold = chunk_into_n(speakers, n=k)

    for fold_index in range(k):
        fold_speakers_ids = set(speaker_ids_per_fold[fold_index])
        with open(MyAPI.dataset_fold_filepath.format(fold_index=str(fold_index)), "w") as file:
            for dialog in dialog_iter_func(fold_index):
                speaker_id = dialog[1][0]
                # Check whether it is a part of the current fold.
                if speaker_id in fold_speakers_ids:
                    MyAPI.write_dataset_buffer(file=file, buffer=dialog)


def dialog_iter_func(fold_index):
    lines_it = MyAPI.read_dataset(
        dataset_filepath=MyAPI.dataset_filepath, split_meta=True, desc="Prepare fold {}".format(fold_index))
    return MyAPI.iter_dataset_as_dialogs(lines_it)


write_folded_dataset(k=MyAPI.dataset_folding_parts,
                     dialog_iter_func=dialog_iter_func,
                     speakers=MyAPI.read_speakers())

print("Original:")
print(MyAPI.calc_speakers_count(dataset_filepath=MyAPI.dataset_filepath, pbar=False))
print("Folds:")
for i in range(MyAPI.dataset_folding_parts):
    c = MyAPI.calc_speakers_count(dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=i), pbar=False)
    print(sum(c.values()))

# Merge foldings.
# We select such indexes for better result balancing.
cat_files(source_filepaths=[MyAPI.dataset_fold_filepath.format(fold_index=str(i)) for i in MyAPI.dataset_train_parts],
          target_filepath=MyAPI.dataset_fold_filepath.format(fold_index="train"))
cat_files(source_filepaths=[MyAPI.dataset_fold_filepath.format(fold_index=str(i)) for i in MyAPI.dataset_valid_parts],
          target_filepath=MyAPI.dataset_fold_filepath.format(fold_index="valid"))

print("---")
for i in ["train", "valid"]:
    c = MyAPI.calc_speakers_count(dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=i), pbar=False)
    print(sum(c.values()))
