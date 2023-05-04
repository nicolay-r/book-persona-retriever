from os.path import join

import utils
import torch
from torch.nn.functional import cross_entropy
from transformers import AdamW, BertTokenizer
from models.mono_bert.model import MonoBERT


model = MonoBERT.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'))
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased", cache_dir=join(utils.PROJECT_DIR, '.transformers'))

optimizer = AdamW(model.parameters(), lr=1e-5, eps=1e-8)
optimizer.zero_grad()

query = "Is response for `{q}` is".format(q="this is a utterance sample")
pos_doc = "This is a response"
neg_doc = "This is a wrong response"

pos_text = "{} [SEP] {}".format(query, pos_doc)
neg_text = "{} [SEP] {}".format(query, neg_doc)

pos_encoded = tokenizer.encode_plus(pos_text, return_tensors="pt")
neg_encoded = tokenizer.encode_plus(neg_text, return_tensors="pt")

pos_output = model.forward(**pos_encoded).squeeze(1)
neg_output = model.forward(**neg_encoded).squeeze(1)

labels = torch.zeros(1, dtype=torch.long)

loss = cross_entropy(torch.stack((pos_output, neg_output), dim=1), labels)

loss.backward()
optimizer.step()