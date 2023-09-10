import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import re
import pyodbc
import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
from dummy import accidents

app = Flask(__name__)
binary_model = tf.keras.models.load_model('training/BERT_Model.h5', custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)
multiclass_model = tf.keras.models.load_model('training/BERT_Model_MultiClass.h5', custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)

cnxn_str = ("Driver={ODBC Driver 18 for SQL Server};"
            "Server=p1wg10891.dc01.its.hpecorp.net,1121;"
            "Database=AMS_AMR;"
            "TrustServerCertificate=yes;"
            "UID=dccadmin;"
            "PWD=AM$GDLMay;")

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
    json = request.get_json()
    #data = json['text']
    data = accidents
    predictions_list = []
    date = ''
    for text in data:
        description = text["descripción"]
        description = clean_text(description)
        description = [translate_text(description)]
        date = datetime.datetime.strptime(text["fecha"], '%d/%m/%Y %I:%M %p')
        predictions = binary_model.predict(description)
        predictions = np.round(predictions.T[0])
        
        if predictions[0] == 0.:
            continue
        else:
            accident_predictions = predict_class(description)
            if accident_predictions[0] == 0:
                accident = 1
            elif accident_predictions[0] == 1:
                accident = 2
            elif accident_predictions[0] == 2:
                accident = 3
            
            prediction = {
                "text": text["descripción"],
                "predictions": accident,
                "date": date,
                "state": 0
            }
            predictions_list.append(prediction)
    
    each_prediction = []
    for item in predictions_list:
        predictions_tuple = (item["text"], item["predictions"], item["date"], item["state"])
        each_prediction.append(predictions_tuple)
    try:
        cnxn = pyodbc.connect(cnxn_str)
        cursor = cnxn.cursor()
        query = f"INSERT INTO [dbo].[zzDB] ([Descripcion], [CtegoriaId], [Fecha], [Estado]) VALUES (?, ?, ?, ?)"
        cursor.executemany(query, each_prediction)
        cnxn.commit()
        cnxn.close()
    except:
        print("No hay publicaciones de precances viales")
    return predictions_list
    


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        #debug=True
    )