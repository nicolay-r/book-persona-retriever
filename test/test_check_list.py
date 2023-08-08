from utils_my import MyAPI

s = set()
print(MyAPI.hla_prompts_filepath)
with open(MyAPI.hla_prompts_filepath, "r") as f:
    for line in f.readlines():
        line = line.split(":")[1]
        words = [s.strip() for s in line.split(",")]
        for w in words:
            s.add(w)

print("Total different words:", len(s))
