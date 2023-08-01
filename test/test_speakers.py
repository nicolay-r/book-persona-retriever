from core.utils import chunk_into_n
from utils_my import MyAPI

l = chunk_into_n(MyAPI.read_speakers(), n=5)
for i in l:
    print(len(i))
print("----")
print(len(l))