import os
import nltk

from api.ldc import LdcAPI


if __name__ == '__main__':

    # Make sure that we have a necessary resource for the library.
    nltk.download('punkt')

    # Launching the `gutenberg_dialog` library.
    cmd = "python3 -m gutenberg_dialog.main -l=en -f1 -e -f2 -dir {books_dir}".format(
        books_dir=LdcAPI.books_storage)

    os.system(cmd)
