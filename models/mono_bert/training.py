from pathlib import Path

import utils
import torch

from os.path import join
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from transformers import AdamW, BertTokenizer, BertModel
from models.mono_bert.model import MonoBERT


#######################################################
# This flag is for debugging and force launching on CPU
#######################################################
# os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

# Replace with MonoBERT
from models.utils import read_raw_texts_and_labels, CustomDataset

model = MonoBERT.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'), num_labels=2)
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'))
optimizer = AdamW(model.parameters(), lr=1e-5, eps=1e-8)

###################################################################################
# Reading raw texts.
###################################################################################
train_texts, train_labels = read_raw_texts_and_labels(utils.RANK_DATASET_DIR)
test_texts, test_labels = read_raw_texts_and_labels(utils.RANK_DATASET_DIR)
train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=.2)

###################################################################################
# Declaring dataset.
###################################################################################
max_input_length = 512
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=max_input_length)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=max_input_length)
test_encodings = tokenizer(test_texts, truncation=True, padding=True, max_length=max_input_length)

train_dataset = CustomDataset(train_encodings, train_labels)
val_dataset = CustomDataset(val_encodings, val_labels)
test_dataset = CustomDataset(test_encodings, test_labels)

###################################################################################
# Start pytorch native training process.
###################################################################################
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model.to(device)
model.train()

train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)

epoch_count = 2
for epoch in range(epoch_count):
    total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        token_type_ids = batch['token_type_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        loss = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
        print(loss)
        exit(0)
        loss.sum().backward()
        optimizer.step()
        total_loss += loss.sum().item()
    print("Epoch: {e}, avg-loss: {l}".format(e=epoch, l=total_loss/len(train_loader)))

model.eval()

# Model Inference
test_loader = DataLoader(test_dataset, batch_size=1)
for batch in test_loader:
    input_ids = batch['input_ids'].to(device)
    token_type_ids = batch['token_type_ids'].to(device)
    attention_mask = batch['attention_mask'].to(device)
    prediction = model(input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)
    prediction = prediction.argmax(dim=-1).item()
    print(prediction)
    #probs = torch.softmax(prediction, dim=1)
