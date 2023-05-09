import os
from utils_ceb import CEBApi

books_dir = CEBApi.books_storage

# Using a side project `gutenberg-dialog` for utterances extraction.
cmd = "python -m gutenberg_dialog.main -l=en -f1 -e -f2 -c -dir {books_dir}".format(books_dir=books_dir)
os.system(cmd)

# remove empty files.
cmd = "find {books_dir} -type f -empty -print -delete".format(books_dir=books_dir)
os.system(cmd)