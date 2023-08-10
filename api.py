import time
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import os
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator

app = Flask(__name__)
model = tf.keras.models.load_model('BERT_Model.h5', custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)

CORS(app)

@app.route("/hello")
def helloWorld():
    return "Hello world"

def translate_text(text, dest='en'):
    translator = Translator()
    translation = translator.translate(text, dest=dest)
    return translation.text

@app.route("/predictedTopics", methods=["GET"])
def getPredictedTopics():
    #json = request.get_json()
    #data = json['text']
    data = "acabo de chocar en mi coche con un camion, que alguien venga por mi"
    text = translate_text(data)
    
    predictions_list = [f'{text}']
    predictions = model.predict(predictions_list)
    predictions = np.round(predictions.T[0])

    if predictions[0] == 0.:
        is_accident = False
    else:
        is_accident = True
    return jsonify({'text': text, 'predictions': is_accident, 'date': time.time()})


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        #debug=True
    )