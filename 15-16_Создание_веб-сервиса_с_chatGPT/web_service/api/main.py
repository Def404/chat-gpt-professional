from fastapi import FastAPI
import os
from dotenv import load_dotenv
import requests
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from openai import OpenAI
from langchain.vectorstores import FAISS
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 

load_dotenv()

key = os.getenv('PROXY_API_KEY')
base_url = os.getenv('PROXY_API_URL')


os.environ["OPENAI_API_KEY"] = key
os.environ["OPENAI_BASE_URL"] = base_url

# Создание клиента OpenAI с использованием API ключа из переменных среды
client = OpenAI()

# функция для загрузки документа по ссылке из гугл драйв
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

data_from_url= load_document_text('https://docs.google.com/document/d/11MU3SnVbwL_rM-5fIC14Lc3XnbAV4rY1Zd_kpcMuH4Y')
system = load_document_text('https://docs.google.com/document/d/1pe8yUe2kScsfxgPKFRbcBKOfXwS7b5rM8NjQDVVdEY0/edit?usp=sharing')

source_chunks=[]
splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=0)
for chunk in splitter.split_text(data_from_url):
    source_chunks.append(Document(page_content=chunk, metadata={}))
print("Общее количество чанков: ", len(source_chunks))

# Инициализирум модель эмбеддингов
embeddings = OpenAIEmbeddings()

# Создадим индексную базу из разделенных фрагментов текста
db = FAISS.from_documents(source_chunks, embeddings)

# Функция, которая позволяет выводить ответ модели в удобочитаемом виде
def insert_newlines(text: str, max_len: int = 170) -> str:
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) > max_len:
            lines.append(current_line)
            current_line = ""
        current_line += " " + word
    lines.append(current_line)
    return " ".join(lines)

def answer_index(system, topic, search_index, temp=1, verbose=1):

    # Поиск релевантных отрезков из базы знаний
    docs = search_index.similarity_search(topic, k=5)
    if verbose: print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if verbose: print('message_content :\n ======================================== \n', message_content)
    client = OpenAI()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Ответь на вопрос сотрудника на основе представленной информации. Не упоминай документ с информацией для ответа сотруднику в ответе. Документ с информацией для ответа сотруднику: {message_content}\n\nВопрос сотрудника: \n{topic}"}
    ]

    if verbose: print('\n ===========================================: ')

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2 
    )
    answer = insert_newlines(completion.choices[0].message.content)
    return answer


app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  
	allow_credentials=True,
	allow_methods=["*"],  
	allow_headers=["*"],  
)

counter_post_answer = 0

class ModelAnswer(BaseModel):
    text: str    

@app.post("/answer")
async def answer(question: ModelAnswer):
    global counter_post_answer
    counter_post_answer += 1
    answer = answer_index(system, question.text, db, verbose=0)
    return {'message': answer}

@app.get("/counter")
async def counter():
    return {"counter": counter_post_answer}