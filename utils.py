import os
from os.path import join

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = join(PROJECT_DIR, "./data/")
TEST_DIR = join(PROJECT_DIR, "./data/test/")
CACHE_DIR = join(PROJECT_DIR, "./.cache")
