from collections import Counter

from utils import cat_files
from utils_my import MyAPI


def write_folded_dataset(k):
    """ Folding with the even splits of the utterances.
    """
    assert(isinstance(k, int))

    buffer = []
    for fold_index in range(k):

        with open(MyAPI.dataset_fold_filepath.format(fold_index=str(fold_index)), "w") as file:

            partners_count = Counter()

            lines_it = MyAPI.read_dataset(
                dataset_filepath=MyAPI.dataset_filepath,
                desc="Prepare for fold {}".format(fold_index))

            for line in lines_it:

                if line is None:
                    buffer.clear()
                    continue

                s_name = MyAPI._get_meta(line)

                buffer.append(line)

                # response of the partner.
                if len(buffer) == 2:

                    # Check whether it is a part of the current fold.
                    if partners_count[s_name] % k == fold_index:
                        MyAPI.write_dataset_buffer(file=file, buffer=buffer)

                    # Count the amount of partners.
                    partners_count[s_name] += 1


write_folded_dataset(k=MyAPI.dataset_folding_parts)

print("Original:")
print(MyAPI.check_speakers_count(dataset_filepath=MyAPI.dataset_filepath, pbar=False))
print("Folds:")
for i in range(MyAPI.dataset_folding_parts):
    c = MyAPI.check_speakers_count(dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=i), pbar=False)
    print(c)
    print(sum(c.values()))

# Merge foldings.
# We select such indexes for better result balancing.
cat_files(source_filepaths=[MyAPI.dataset_fold_filepath.format(fold_index=str(i)) for i in MyAPI.dataset_train_parts],
          target_filepath=MyAPI.dataset_fold_filepath.format(fold_index="train"))
cat_files(source_filepaths=[MyAPI.dataset_fold_filepath.format(fold_index=str(i)) for i in MyAPI.dataset_valid_parts],
          target_filepath=MyAPI.dataset_fold_filepath.format(fold_index="valid"))
