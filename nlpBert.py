import pandas as pd
import numpy as np
import re

# Huggingface transformers
import transformers
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup

import torch
from torch import nn, cuda
from torch.utils.data import DataLoader, Dataset, RandomSampler, SequentialSampler

import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

BERT_MODEL_NAME = 'bert-base-cased'

tokenizer = BertTokenizer.from_pretrained(BERT_MODEL_NAME)

MAX_TEXT_LEN = 512

from TextCleaner import pretty

def tokenize(text):
    text = pretty(text)

    return tokenizer.encode_plus(
        text,
        None,
        add_special_tokens=True,
        max_length=MAX_TEXT_LEN,
        padding='max_length',
        return_token_type_ids=False,
        return_attention_mask=True,
        truncation=True,
        return_tensors='pt'
    )