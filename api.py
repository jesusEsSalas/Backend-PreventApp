import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import re

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

def clean_text(text):
    emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"
                                u"\U0001F300-\U0001F5FF"
                                u"\U0001F680-\U0001F6FF"
                                u"\U0001F1E0-\U0001F1FF"
                                u"\U00002702-\U000027B0"
                                u"\U000024C2-\U0001F251"
                                "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)

    url = re.compile(r'https?://\S+|www\.\S+')
    text = url.sub(r'',text)

    text = text.replace('#',' ')
    text = text.replace('@',' ')
    symbols = re.compile(r'[^A-Za-z0-9 ]')
    text = symbols.sub(r'',text)

    return text

@app.route("/predictedTopics", methods=["GET"])
def getPredictedTopics():
    #json = request.get_json()
    #data = json['text']
    data = ""
    data = clean_text(data)
    text = translate_text(data)
    
    predictions_list = [f'{text}']
    predictions = binary_model.predict(predictions_list)
    predictions = np.round(predictions.T[0])
    accident = ''
    if predictions[0] == 0.:
        is_accident = False
        return jsonify({'text': text, 'predictions': is_accident})
    else:
        is_accident = True
        accident_predictions = predict_class(predictions_list)
        if accident_predictions[0] == 0:
            accident = 'traffic accident'
        elif accident_predictions[0] == 1:
            accident = 'fire'
        elif accident_predictions[0] == 2:
            accident = 'traffic light'
        
        return jsonify({'text': text, 'predictions': is_accident, 'type': accident})


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        #debug=True
    )