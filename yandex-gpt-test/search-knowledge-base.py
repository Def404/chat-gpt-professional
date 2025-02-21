import requests
import numpy as np
from scipy.spatial.distance import cdist
import re
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.docstore.document import Document

FOLDER_ID = "b1g4ftb11h6q95h77rnk"
API_TOKEN = "AQVN2pFlKlEPq6jcHHi1IJ0w8RofrSSh4NBixT4A"
doc_uri = f"emb://{FOLDER_ID}/text-search-doc/latest"
query_uri = f"emb://{FOLDER_ID}/text-search-query/latest"
embed_url = "https://llm.api.cloud.yandex.net:443/foundationModels/v1/textEmbedding"
headers = {"Content-Type": "application/json", "Authorization": f"Api-Key {API_TOKEN}", "x-folder-id": f"{FOLDER_ID}"}

def load_document_text(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    # Download the document as plain text
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text

    return text

# База знаний, которая будет подаваться в langChain
data_from_url= load_document_text('https://docs.google.com/document/d/1q4l912Re8zuIfBax4FDS3ZppYmVPzER3Si2wrmznddc')
data_from_url[:2000]



system = load_document_text('https://docs.google.com/document/d/1_o3vkYQePIclywlAPSSZyclpe7gLLh3M8MJx7FbM-Yo/edit?usp=sharing')
print(system[:1000])

source_chunks = []
splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=1)

for chunk in splitter.split_text(data_from_url):
    source_chunks.append(Document(page_content=chunk, metadata={}))

def get_embedding(text: str, text_type: str = "doc") -> np.array:
    query_data = {
        "modelUri": doc_uri if text_type == "doc" else query_uri,
        "text": text,
    }

    response = requests.post(embed_url, json=query_data, headers=headers)
    
    if response.status_code != 200:
        print(f"Ошибка {response.status_code}: {response.text}")
        return np.zeros(768)  # Возвращаем пустой вектор нужного размера
    
    data = response.json()
    
    if "embedding" not in data:
        print(f"Ошибка: ключ 'embedding' отсутствует в ответе API: {data}")
        return np.zeros(768)
    
    return np.array(data["embedding"])

query_text1 = "Чем должна располагать специализированная организация?"

query_embedding1 = get_embedding(query_text1, text_type="query")
docs_embedding = [get_embedding(fragment.page_content) for fragment in source_chunks]

# Вычисляем косинусное расстояние
dist = cdist(query_embedding1[None, :], docs_embedding, metric="cosine")

# Вычисляем косинусное сходство
sim = 1 - dist

# most similar doc text
print(query_text1)
print(source_chunks[np.argmax(sim)])

print("====")


query_text2 = "Что обязана делать огранизация при эксплуатации ПС?"

query_embedding2 = get_embedding(query_text2, text_type="query")

# Вычисляем косинусное расстояние
dist = cdist(query_embedding1[None, :], docs_embedding, metric="cosine")

# Вычисляем косинусное сходство
sim = 1 - dist

# most similar doc text
print(query_text2)
print(source_chunks[np.argmax(sim)])

print("====")

query_text3 = "Какие требования нужны для установка кранов, передвигающихся по надземному рельсовому пути?"

query_embedding3 = get_embedding(query_text3, text_type="query")

# Вычисляем косинусное расстояние
dist = cdist(query_embedding1[None, :], docs_embedding, metric="cosine")

# Вычисляем косинусное сходство
sim = 1 - dist

# most similar doc text
print(query_text3)
print(source_chunks[np.argmax(sim)])

print("====")