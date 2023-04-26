from datasets import load_dataset

dataset = load_dataset("nomic-ai/gpt4all_prompt_generations",
                       cache_dir="./data/huggingface/datasets")

print(dataset.num_rows)
print(dataset.column_names)

select_result = dataset.select_columns("source")
print(type(select_result))

sources_set = set()
for r in select_result['train'].iter(1):
    sources_set.add(r['source'][0])

print(sources_set)