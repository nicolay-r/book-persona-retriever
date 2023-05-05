from pathlib import Path

import torch


def read_raw_texts_and_labels(root_dir):
    texts = []
    labels = []
    for text_file in Path(root_dir).iterdir():
        with open(text_file, 'r') as f:
            for i, line in enumerate(f.readlines()):
                texts.append(line)
                labels.append(i%2)

    return texts, labels


class CustomDataset(torch.utils.data.Dataset):
    """ Declare our own dataset.
    """

    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)
