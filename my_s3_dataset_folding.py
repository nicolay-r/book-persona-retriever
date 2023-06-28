from collections import Counter

from utils_my import MyAPI


def write_folded_dataset(my_api, k):
    """ Folding with the even splits of the utterances.
    """
    assert(isinstance(my_api, MyAPI))
    assert(isinstance(k, int))

    buffer = []
    for fold_index in range(k):

        with open(my_api.dataset_fold_filepath.format(fold_index=str(fold_index)), "w") as file:

            partners_count = Counter()

            for line in my_api.read_dataset(desc="Prepare for fold {}".format(fold_index)):

                if line is None:
                    buffer.clear()
                    continue

                s_name = my_api._get_meta(line)

                buffer.append(line)

                # response of the partner.
                if len(buffer) == 2:

                    # Check whether it is a part of the current fold.
                    if partners_count[s_name] % k == fold_index:
                        my_api.write_dataset_buffer(file=file, buffer=buffer)

                    # Count the amount of partners.
                    partners_count[s_name] += 1


k = 5
my_api = MyAPI()
write_folded_dataset(my_api, k=k)

print("Original:")
print(my_api.check_speakers_count(filepath=my_api.dataset_filepath, pbar=False))
print("Folds:")
for i in range(k):
    c = my_api.check_speakers_count(filepath=my_api.dataset_fold_filepath.format(fold_index=i), pbar=False)
    print(c)
    print(sum(c.values()))
