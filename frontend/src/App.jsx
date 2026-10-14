import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

export default function App() {
  const webcamRef = useRef(null);
  const [nome, setNome] = useState('');
  const [matricula, setMatricula] = useState('');
  const [cargo, setCargo] = useState('');
  const [mensagem, setMensagem] = useState('');

  const capturarImagem = () => {
    return webcamRef.current.getScreenshot();
  };

  const handleCadastrar = async () => {
    const imagemBase64 = capturarImagem();
    try {
      const resposta = await axios.post('http://localhost:8000/cadastrar', {
        nome,
        matricula,
        cargo,
        imagem_base64: imagemBase64
      });
      setMensagem(resposta.data.mensagem);
    } catch (erro) {
      setMensagem("Erro ao cadastrar funcionário.");
    }
  };

  const handleRegistrarPonto = async (tipo) => {
    const imagemBase64 = capturarImagem();
    try {
      const resposta = await axios.post('http://localhost:8000/registrar-ponto', {
        imagem_base64: imagemBase64,
        tipo: tipo
      });
      setMensagem(`${resposta.data.mensagem} às ${resposta.data.data_hora}`);
    } catch (erro) {
      setMensagem(erro.response?.data?.detail || "Erro ao registar o ponto.");
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>Sistema de Registo de Ponto Facial</h1>
      
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={400}
      />

      <div style={{ marginTop: '20px' }}>
        <h2>1. Cadastro de Funcionário</h2>
        <input type="text" placeholder="Nome" value={nome} onChange={e => setNome(e.target.value)} /><br/>
        <input type="text" placeholder="Matrícula" value={matricula} onChange={e => setMatricula(e.target.value)} /><br/>
        <input type="text" placeholder="Cargo" value={cargo} onChange={e => setCargo(e.target.value)} /><br/>
        <button onClick={handleCadastrar}>Capturar Rosto e Cadastrar</button>
      </div>

      <div style={{ marginTop: '20px' }}>
        <h2>2. Registo de Ponto</h2>
        <button onClick={() => handleRegistrarPonto('Entrada')}>Registar Entrada</button>
        <button onClick={() => handleRegistrarPonto('Intervalo')}>Registar Intervalo</button>
        <button onClick={() => handleRegistrarPonto('Saída')}>Registar Saída</button>
      </div>

      {mensagem && <p style={{ fontWeight: 'bold', color: 'blue' }}>{mensagem}</p>}
    </div>
  );
}