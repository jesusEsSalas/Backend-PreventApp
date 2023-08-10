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

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
device = torch.device("cpu")

TOPICS = [
    "traffic accident",
    "fire",
    "traffic light"
]

from sklearn.preprocessing import MultiLabelBinarizer
mlb = MultiLabelBinarizer()
mlb.fit([TOPICS])

from AccidentsClassifier import AccidentsClassifier

TRAINED_MODEL_NAME = "multilabel-model.ckpt"
PATH = f"training/{TRAINED_MODEL_NAME}"
TRESHOLD = 0.46

import nlpBert

class MultiLabelClassification:
    def __init__(self):
        self.model = AccidentsClassifier(num_classes=len(TOPICS))

        self.model = self.model.load_from_checkpoint(PATH)

        self.model = self.model.to(device)
        self.model.eval()
        print("MultiLabel Model is ready to use")

    def classify(self, predictions, treshold):
        y_pred = []
        for pred in predictions:
            y_pred.append([bool(label >= treshold) for label in pred])
        return np.array(y_pred)
    
    def predict(self, problem_statement):
        encoded = nlpBert.tokenize(problem_statement)

        predictions_prob = self.model(encoded['input_ids'], encoded['attention_mask'])
        predictions_prob = torch.sigmoid(predictions_prob)

        predictions_prob = predictions_prob.detach().cpu().numpy()

        predictions = self.classify(predictions_prob, TRESHOLD)
        predictions_prob = [prob for prob, pred in zip(predictions_prob[0], predictions[0]) if pred]

        actual_prediction = mlb.inverse_transform(predictions)
        actual_prediction = np.asarray(actual_prediction[0])

        prediction_with_probability = [{
            'target': target,
            'probability': round(float(prob * 100), 2),
        } for target, prob in zip(actual_prediction, predictions_prob)]

        return prediction_with_probability

from dummy import static_problems
model = MultiLabelClassification()
for i in range(0, 5):
    print(static_problems[i]['history'])
    print(f"Predicted {model.predict(static_problems[i]['history'])}")
    print(f"Real {static_problems[i]['history']}")
    print()