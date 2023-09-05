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
binary_model = tf.keras.models.load_model('training/BERT_Model.h5', custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)
multiclass_model = tf.keras.models.load_model('training/BERT_Model_MultiClass.h5', custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)

CORS(app)

@app.route("/hello")
def helloWorld():
    return "Hello world"

def translate_text(text, dest='en'):
    translator = Translator()
    translation = translator.translate(text, dest=dest)
    return translation.text

def predict_class(accidents):
    return [np.argmax(pred) for pred in multiclass_model.predict(accidents)]

@app.route("/predictedTopics", methods=["GET"])
def getPredictedTopics():
    #json = request.get_json()
    #data = json['text']
    data = "#almomento Conductores reportan una columna de humo sobre la Glorieta Colón. Solicitamos a Protección Civil y Bomberos GDL atender el reporte."
    text = translate_text(data)
    
    predictions_list = [f'{text}']
    predictions = binary_model.predict(predictions_list)
    predictions = np.round(predictions.T[0])
    accident = ''
    if predictions[0] == 0.:
        is_accident = False
        return jsonify({'text': text, 'predictions': is_accident, 'date': time.time()})
    else:
        is_accident = True
        accident_predictions = predict_class(predictions_list)
        if accident_predictions[0] == 0:
            accident = 'traffic accident'
        elif accident_predictions[0] == 1:
            accident = 'fire'
        elif accident_predictions[0] == 2:
            accident = 'traffic light'
        
        return jsonify({'text': text, 'predictions': is_accident, 'type': accident, 'date': time.time()})


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        #debug=True
    )