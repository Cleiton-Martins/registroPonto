from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deepface import DeepFace
import sqlite3
import base64
import cv2
import numpy as np
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if not os.path.exists("db_rostos"):
    os.makedirs("db_rostos")

conn = sqlite3.connect('ponto.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        matricula TEXT UNIQUE,
        cargo TEXT,
        caminho_foto TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS registos_ponto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula TEXT,
        data_hora TEXT,
        tipo TEXT
    )
''')
conn.commit()

class Funcionario(BaseModel):
    nome: str
    matricula: str
    cargo: str
    imagem_base64: str 

class Ponto(BaseModel):
    imagem_base64: str
    tipo: str 

def descodificar_imagem(base64_string, caminho_salvar):
    imagem_dados = base64.b64decode(base64_string.split(',')[1])
    nparr = np.frombuffer(imagem_dados, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite(caminho_salvar, img)
    return caminho_salvar

@app.post("/cadastrar")
async def cadastrar_funcionario(func: Funcionario):
    caminho_foto = f"db_rostos/{func.matricula}.jpg"
    descodificar_imagem(func.imagem_base64, caminho_foto)
    
    try:
        cursor.execute("INSERT INTO funcionarios (nome, matricula, cargo, caminho_foto) VALUES (?, ?, ?, ?)",
                       (func.nome, func.matricula, func.cargo, caminho_foto))
        conn.commit()
        return {"mensagem": "Funcionário cadastrado com sucesso!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Matrícula já existente.")

@app.post("/registrar-ponto")
async def registrar_ponto(ponto: Ponto):
    caminho_temporario = "temp.jpg"
    descodificar_imagem(ponto.imagem_base64, caminho_temporario)
    
    try:
        resultados = DeepFace.find(img_path=caminho_temporario, db_path="db_rostos", enforce_detection=False)
        
        if len(resultados) > 0 and len(resultados[0]) > 0:
            # Extrair a matrícula do nome do ficheiro encontrado
            ficheiro_encontrado = resultados[0].iloc[0]['identity']
            matricula = os.path.basename(ficheiro_encontrado).split('.')[0]
            
            data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("INSERT INTO registos_ponto (matricula, data_hora, tipo) VALUES (?, ?, ?)",
                           (matricula, data_hora_atual, ponto.tipo))
            conn.commit()
            
            return {"mensagem": f"Ponto registado para a matrícula {matricula}", "data_hora": data_hora_atual}
        else:
            raise HTTPException(status_code=404, detail="Rosto não reconhecido na base de dados.")
    finally:
        if os.path.exists(caminho_temporario):
            os.remove(caminho_temporario)