from os.path import join, dirname, realpath


class GuttenbergDialogApi:

    __current_dir = dirname(realpath(__file__))
    dialogs_en = join(__current_dir, "./data/filtered/en/dialogs_clean.txt")
