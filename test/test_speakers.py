from api.ldc import LdcAPI
from core.utils import chunk_into_n

l = chunk_into_n(LdcAPI.read_speakers(), n=5)
for i in l:
    print(len(i))
print("----")
print(len(l))