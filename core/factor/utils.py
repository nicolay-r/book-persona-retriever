from tqdm import tqdm


def melt_to_csv(X, y, out_filepath, user_col_name, feature_col_name, value_col_name, sep=",",
                filter_func=lambda val: val > 0.3 or val < -0.3):

    with open(out_filepath, "w") as out:

        # Writing header.
        header = sep.join([user_col_name, feature_col_name, value_col_name])
        out.write(header)
        out.write("\n")

        for user_index, name in tqdm(enumerate(y)):
            for item_ind, feature_value in enumerate(X[user_index]):

                # We use this limitation to guarantee that there is a one criteria for every speaker,
                # and hence the result amount of speakers will remain the same.
                if item_ind > 0:
                    if not filter_func(feature_value):
                        continue

                # Writing content line.
                out.write(sep.join([str(user_index), str(item_ind), str(round(feature_value, 2))]))
                out.write("\n")
