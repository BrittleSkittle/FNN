from newspaper import Article
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from gpt2 import client
from pickle import dump
from pickle import load

title = 0
summary = 1
text = 2
images = 3
url_num = 4
collection = u'articles'


def get_data(url):
    article = Article(url)
    article.download()
    article.parse()
    doc_ref = db.collection(collection).document(article.title)
    doc_ref.set(
        {
            u'title': article.title,
            u'summary': article.summary,
            u'text': article.text,
            u'images': str(article.imgs)
        }
    )


def read_all(col):
    col_ref = db.collection(collection).stream()
    read_list = []
    for doc in col_ref:
        info = doc.get(col)
        print(info)
        read_list.append(info)
    return read_list


project_id = 'fakenewsnetwork-54538'
cred = credentials.Certificate('FNNcred.json')
firebase_admin.initialize_app(cred, {
  'projectId': project_id,
})
db = firestore.client()
con = True
while con:
    user_com = input('Input Url\n')
    if user_com == 'stop':
        con = not con
    elif user_com == 'read text':
        read_all('text')
    elif user_com == 'read title':
        read_all('title')
    else:
        get_data(user_com)


