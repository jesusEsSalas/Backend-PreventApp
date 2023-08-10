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

class AccidentsClassifier(pl.LightningModule):
    # Set up the classifier
    def __init__(self, num_classes, steps_per_epoch=None, num_epochs=3, lr=2e-5):
        super().__init__()

        self.bert = BertModel.from_pretrained(BERT_MODEL_NAME, return_dict=True)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes) # outputs = number of labels
        self.steps_per_epoch = steps_per_epoch
        self.num_epochs = num_epochs
        self.lr = lr
        self.criterion = nn.BCEWithLogitsLoss()

    def forward(self, input_ids, attn_mask):
        output = self.bert(input_ids = input_ids, attention_mask = attn_mask)
        output = self.classifier(output.pooler_output)

        return output

    def training_step(self, batch, batch_idx):
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        labels = batch['label']

        outputs = self(input_ids,attention_mask)
        loss = self.criterion(outputs,labels)
        self.log('train_loss', loss, prog_bar=True, logger=True)

        return {"loss": loss, "predictions": outputs, "labels": labels }

    def validation_step(self,batch,batch_idx):
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        labels = batch['label']

        outputs = self(input_ids,attention_mask)
        loss = self.criterion(outputs,labels)
        self.log('val_loss', loss, prog_bar=True, logger=True)

        return loss

    def test_step(self,batch,batch_idx):
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        labels = batch['label']

        outputs = self(input_ids,attention_mask)
        loss = self.criterion(outputs,labels)
        self.log('test_loss', loss, prog_bar=True, logger=True)

        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr = self.lr)
        warmup_steps = self.steps_per_epoch//3
        total_steps = self.steps_per_epoch * self.num_epochs - warmup_steps

        scheduler = get_linear_schedule_with_warmup(optimizer,warmup_steps,total_steps)

        return [optimizer], [scheduler]