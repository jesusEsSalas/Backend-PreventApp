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

cnxn_str = ("Driver={FreeTDS};"
            "Server=10.92.240.6,1433;"
            "Database=PreventAppDb;"
            "TrustServerCertificate=yes;"
            "UID=sqlserver;"
            "PWD=PreventApp@Project;"
            "Encrypt=no")

CORS(app)

@app.route("/")
def message():
    return "App running"

@app.route("/prueba", methods=["GET"])
def toDB():
    predictions_list = []
    date = datetime.datetime.now()
        
    prediction = {
        "text": "⚠️Choque entre dos vehículos en la Glorieta Colón ubicada entre la avenida Américas y López Mateos; Tómalo en cuenta si circulas por la zona #ReporteZMG",
        "predictions": 1,
        "date": date,
        "state": 0
    }
            
    predictions_list.append(prediction)
    
    each_prediction = []
    for item in predictions_list:
        predictions_tuple = (item["text"], item["date"], item["state"], item["predictions"])
        each_prediction.append(predictions_tuple)
    try:
        cnxn = pyodbc.connect(cnxn_str)
        cursor = cnxn.cursor()
        query = f"INSERT INTO [dbo].[Accidentes] ([Descripcion], [Fecha], [Estado], [CategoriaId]) VALUES (?, ?, ?, ?)"
        cursor.executemany(query, each_prediction)
        cnxn.commit()
        cnxn.close()
        return predictions_list, 200
    except Exception as e:
        print(e)
        return f"No hay publicaciones de precances viales\n{e}", 500

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

@app.route("/predictedTopics", methods=["GET", "POST"])
def getPredictedTopics():
    json = request.get_json()
    data = json
    predictions_list = []
    date = ''
    for text in data:
        description = text["descripcion"]
        description = clean_text(description)
        description = [translate_text(description)]
        date = text["fecha"]
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
                "text": text["descripcion"],
                "predictions": accident,
                "date": date,
                "state": 0
            }
            predictions_list.append(prediction)
    
    each_prediction = []
    for item in predictions_list:
        predictions_tuple = (item["text"], item["date"], item["state"], item["predictions"])
        each_prediction.append(predictions_tuple)
    try:
        cnxn = pyodbc.connect(cnxn_str)
        cursor = cnxn.cursor()
        query = f"INSERT INTO [dbo].[Accidentes] ([Descripcion], [Fecha], [Estado], [CategoriaId]) VALUES (?, ?, ?, ?)"
        cursor.executemany(query, each_prediction)
        cnxn.commit()
        cnxn.close()
        return predictions_list, 200
    except Exception as e:
        print(e)
        return "No hay publicaciones de precances viales", 500
    


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        #debug=True
    )
