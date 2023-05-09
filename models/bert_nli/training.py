import utils
import torch
from os.path import join
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from transformers import BertModel, AdamW, BertTokenizer
from models.bert_nli.model import BERTNLIModel
from models.utils import read_raw_texts_and_labels, CustomDataset


max_input_length = 512
output_dim = 2
model = BertModel.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'))
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'))
nli_model = BERTNLIModel(model, output_dim=output_dim)

###################################################################################
# Reading raw texts.
###################################################################################
train_texts, train_labels = read_raw_texts_and_labels(utils.RANK_DATASET_DIR)
test_texts, test_labels = read_raw_texts_and_labels(utils.RANK_DATASET_DIR)
train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=.2)

###################################################################################
# Tokenize data.
###################################################################################
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=max_input_length)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=max_input_length)
test_encodings = tokenizer(test_texts, truncation=True, padding=True, max_length=max_input_length)

###################################################################################
# Declaring dataset.
###################################################################################
train_dataset = CustomDataset(train_encodings, train_labels)
val_dataset = CustomDataset(val_encodings, val_labels)
test_dataset = CustomDataset(test_encodings, test_labels)

###################################################################################
# Start training process.
###################################################################################
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
nli_model.to(device)
nli_model.train()

train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
optimizer = AdamW(model.parameters(), lr=1e-5, eps=1e-8)
criterion = torch.nn.CrossEntropyLoss().to(device)


def train(model, iterator, optimizer, criterion):
    epoch_loss = 0
    epoch_acc = 0
    model.train()
    for batch in iterator:
        optimizer.zero_grad()        # clear gradients first
        torch.cuda.empty_cache()     # releases all unoccupied cached memory
        input_ids = batch['input_ids'].to(device)
        attn_mask = batch['attention_mask'].to(device)
        token_type = batch['token_type_ids'].to(device)
        label = batch['labels'].to(device)
        predictions = model(input_ids, attn_mask, token_type)
        loss = criterion(predictions, label)
        acc = categorical_accuracy(predictions, label)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
        epoch_acc += acc.item()
    return epoch_loss / len(iterator), epoch_acc / len(iterator)


def categorical_accuracy(preds, y):
    max_preds = preds.argmax(dim=1, keepdim=True)
    correct = (max_preds.squeeze(1)==y).float()
    return correct.sum() / len(y)


for e in range(20):
    result = train(nli_model, iterator=train_loader, optimizer=optimizer, criterion=criterion)
    print(result)

# for epoch in range(6):
#    total_loss = 0
#    for batch in train_loader:
#        optimizer.zero_grad()
#        input_ids = batch['input_ids'].to(device)
#        token_type_ids = batch['token_type_ids'].to(device)
#        attention_mask = batch['attention_mask'].to(device)
#        labels = batch['labels'].to(device)
#        predictions = nli_model(input_ids, attention_mask, token_type_ids)
#        loss = criterion(predictions, labels)
#        acc = categorical_accuracy(predictions, labels)
#        optimizer.step()
#        total_loss += loss.sum().item()
#    print("Epoch: {e}, avg-loss: {l}".format(e=epoch, l=total_loss/len(train_loader)))


