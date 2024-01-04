import numpy as np
import pandas as pd
from pickle import dump
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Input, Dense, LSTM, SimpleRNN
from keras.models import Model
from pickle import load
from keras.models import load_model
from keras.utils import to_categorical
from keras.preprocessing.sequence import pad_sequences
import random

headlines = []
new_headlines = []
with open("headlines.txt", "r") as f:
    headlines = f.readlines()
for i in range(len(headlines)):
    headlines[i] = headlines[i].strip('\n')
# for i in range(len(headlines)):
#     headlines[i]=headlines[i].split(" ")
headlines = np.array(headlines)
# print(headlines)
df = pd.DataFrame(headlines)
# print(df)
text = df[0]
text_size = len(text)
# print('Text Size: %d' % text_size)

chars = sorted(list(set(text)))
mapping = dict((c, i) for i, c in enumerate(chars))
dump(mapping, open('mapping.pkl', 'wb'))

vocab_size = len(mapping)
print('Vocabulary Size: %d' % vocab_size)

encoded_text = [mapping[char] for char in text]
encode_size = len(encoded_text)
print('Code Size: %d' % encode_size)

seq_len = 10
batch_size = 512
batch_num = int((encode_size - seq_len) / batch_size)


def my_generator():
    while 1:
        for k in range(batch_num):
            x_batch = []
            y_batch = []
            for j in range(batch_size):
                x_batch.append(encoded_text[k * batch_size + j:k * batch_size + j + seq_len])
                y_batch.append(encoded_text[k * batch_size + j + seq_len:k * batch_size + j + seq_len + 1])

            x_batch = np.array([to_categorical(x, num_classes=vocab_size) for x in x_batch])
            y_batch = np.array(to_categorical(y_batch, num_classes=vocab_size))

            yield x_batch, y_batch


model = Sequential()
model.add(LSTM(300, return_sequences=True, input_shape=(seq_len, vocab_size)))
model.add(LSTM(150, return_sequences=True))
model.add(LSTM(75))
model.add(Dense(vocab_size, activation='softmax'))
print(model.summary())


my_generator = my_generator()
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit_generator(my_generator, steps_per_epoch=batch_num, epochs=10, verbose=1)
model.save('model_3lay.h5')


def generate_seq(model, mapping, seq_length, seed_text, n_chars):
    in_text = seed_text
    for _ in range(n_chars):
        encoded = [mapping[char2] for char2 in in_text]
        encoded = pad_sequences([encoded], maxlen=seq_length, truncating='pre')
        encoded = to_categorical(encoded, num_classes=len(mapping))
        prob = model.predict_proba(encoded)
        y_hat = random.choices(range(0, vocab_size), weights=prob[0], k=1)[0]
        out_char = ''
        for char, index in mapping.items():
            if index == y_hat:
                out_char = char
                break
        in_text += out_char
        if char == "\n":
            break
    return in_text


model = load_model('model_3lay.h5')
mapping = load(open('mapping.pkl', 'rb'))

print(generate_seq(model, mapping, seq_len, 'Trump tells', 400))

