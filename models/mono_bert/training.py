from os.path import join
from pathlib import Path
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

import utils
import torch
from transformers import AdamW, BertTokenizer
from models.mono_bert.model import MonoBERT


model = MonoBERT.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'), num_labels=2)
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'))
optimizer = AdamW(model.parameters(), lr=1e-5, eps=1e-8)


# pos_encoded = tokenizer.encode_plus(pos_text, return_tensors="pt")
# neg_encoded = tokenizer.encode_plus(neg_text, return_tensors="pt")

###################################################################################
# Reading raw texts.
###################################################################################
def read_raw_texts_and_labels(root_dir):
    texts = []
    labels = []
    for text_file in Path(root_dir).iterdir():
        with open(text_file, 'r') as f:
            for line in f.readlines():
                texts.append(line)
                labels.append(1)

    return texts, labels


train_texts, train_labels = read_raw_texts_and_labels(utils.RANK_DATASET_DIR)
test_texts, test_labels = read_raw_texts_and_labels(utils.RANK_DATASET_DIR)
train_texts, val_texts, train_labels, val_labels = train_test_split(
    train_texts, train_labels, test_size=.2)


###################################################################################
# Declaring dataset.
###################################################################################
class CustomDataset(torch.utils.data.Dataset):

    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)
test_encodings = tokenizer(test_texts, truncation=True, padding=True)

train_dataset = CustomDataset(train_encodings, train_labels)
val_dataset = CustomDataset(val_encodings, val_labels)
test_dataset = CustomDataset(test_encodings, test_labels)

###################################################################################
# Start pytorch native training process.
###################################################################################
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model.to(device)
model.train()

train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)

for epoch in range(3):
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        print(input_ids)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        outputs = model(input_ids,
                        attention_mask=attention_mask,
                        token_type_ids=input_ids)
        loss = outputs[0]
        loss.backward()
        optimizer.step()

model.eval()