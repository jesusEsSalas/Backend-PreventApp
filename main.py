import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import os
from googletrans import Translator

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def translate_text(text, dest='en'):
    translator = Translator()
    translation = translator.translate(text, dest=dest)
    return translation.text

model = tf.keras.models.load_model('BERT_Model.h5', custom_objects={'KerasLayer': hub.KerasLayer}, compile=False)
#model.compile()
spanish = 'Aquí tomandome un helado agusto en la calle avila camacho'
text = translate_text(spanish)

predictions_list = [f'{text}']

predictions = model.predict(predictions_list)
predictions = np.round(predictions.T[0])

print(predictions)
