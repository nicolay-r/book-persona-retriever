import os

from utils_ceb import CEBApi

# Using a side project `gutenberg-dialog` for utterances extraction.
cmd = "python3 service/gutenberg-dialog/code/main.py -l=en -f1 -e -f2 -c -dir {books_dir}".format(
    books_dir=CEBApi.books_storage)
os.system(cmd)