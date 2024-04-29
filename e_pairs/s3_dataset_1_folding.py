from tqdm import tqdm

from api.my import MyAPI
from core.utils import chunk_into_n
from utils import cat_files


def write_folded_dataset(k, dialog_iter_func, speakers):
    """ Folding with the even splits of the utterances.
    """
    assert(isinstance(k, int))
    assert(isinstance(speakers, list))
    assert(callable(dialog_iter_func))

    speaker_ids_per_fold = chunk_into_n(speakers, n=k)

    for fold_index in range(k):
        fold_speakers_ids = set(speaker_ids_per_fold[fold_index])
        target = MyAPI.dataset_fold_filepath.format(fold_index=str(fold_index))
        with open(target, "w") as file:
            for dialog in dialog_iter_func(fold_index):
                speaker_id = dialog[1][0]
                # Check whether it is a part of the current fold.
                if speaker_id in fold_speakers_ids:
                    MyAPI.write_dataset_buffer(file=file, buffer=dialog)
        print(f"Fold written: {target}")


def dialog_iter_func(fold_index):
    lines_it = MyAPI.read_dataset(
        dataset_filepath=MyAPI.dataset_filepath, split_meta=True, desc="Prepare fold {}".format(fold_index))
    return tqdm(MyAPI.iter_dataset_as_dialogs(lines_it), "Filter question-response pairs")


if __name__ == '__main__':

    write_folded_dataset(k=MyAPI.dataset_folding_parts,
                         dialog_iter_func=dialog_iter_func,
                         speakers=MyAPI.read_speakers())

    print("------------------------------------------")
    print("Original amount of utterances per speaker:")
    print(MyAPI.calc_utterances_per_speakers_count(dataset_filepath=MyAPI.dataset_filepath, pbar=False))

    print("-----------------------------------------")
    print("Folds sizes (total amount of utterances):")
    for fold_index in range(MyAPI.dataset_folding_parts):
        c = MyAPI.calc_utterances_per_speakers_count(
            dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=fold_index),
            pbar=False)
        print(f"Fold#{fold_index}:", sum(c.values()), "utterances")

    print("=>")

    # We select such indexes for better result balancing.
    for fold_name, fold_parts in MyAPI.dataset_folding_fixed_parts.items():

        target = MyAPI.dataset_fold_filepath.format(fold_index=fold_name)
        cat_files(source_filepaths=[MyAPI.dataset_fold_filepath.format(fold_index=str(i)) for i in fold_parts],
                  target_filepath=target)

        c = MyAPI.calc_utterances_per_speakers_count(
            dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=fold_name),
            pbar=False)

        print(f"Total amount of utterances for `{fold_name}` ({fold_parts}) split:", sum(c.values()))
        print(f"Saved: {target}")
