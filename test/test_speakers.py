from api.my import MyAPI
from core.utils import chunk_into_n

l = chunk_into_n(MyAPI.read_speakers(), n=5)
for i in l:
    print(len(i))
print("----")
print(len(l))