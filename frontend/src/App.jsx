import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [candidatos, setCandidatos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    telefone: '',
    experiencia: ''
  });
  const [editando, setEditando] = useState(null);
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');

  useEffect(() => {
    carregarCandidatos();
  }, []);

  const carregarCandidatos = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/candidatos`);
      const data = await response.json();
      setCandidatos(data);
    } catch (error) {
      setErro('Erro ao carregar candidatos');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setSucesso('');
    setLoading(true);

    try {
      const url = editando 
        ? `${API_BASE_URL}/candidatos/${editando}`
        : `${API_BASE_URL}/candidatos`;
      
      const method = editando ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setSucesso(editando ? 'Candidato atualizado com sucesso!' : 'Candidato cadastrado com sucesso!');
        setFormData({ nome: '', email: '', telefone: '', experiencia: '' });
        setEditando(null);
        carregarCandidatos();
      } else {
        setErro(data.detail?.erro || 'Erro ao salvar candidato');
      }
    } catch (error) {
      setErro('Erro de conexão com a API');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (candidato) => {
    setFormData({
      nome: candidato.nome,
      email: candidato.email,
      telefone: candidato.telefone || '',
      experiencia: candidato.experiencia || ''
    });
    setEditando(candidato.id);
    setErro('');
    setSucesso('');
  };

  const handleDelete = async (id, nome) => {
    if (!window.confirm(`Tem certeza que deseja excluir ${nome}?`)) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/candidatos/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setSucesso('Candidato excluído com sucesso!');
        carregarCandidatos();
      } else {
        const data = await response.json();
        setErro(data.detail?.erro || 'Erro ao excluir candidato');
      }
    } catch (error) {
      setErro('Erro de conexão com a API');
    } finally {
      setLoading(false);
    }
  };

  const cancelarEdicao = () => {
    setFormData({ nome: '', email: '', telefone: '', experiencia: '' });
    setEditando(null);
    setErro('');
    setSucesso('');
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Sistema de Candidatos</h1>
      </header>

      <main className="app-main">
        <div className="form-section">
          <h2>{editando ? 'Editar Candidato' : 'Cadastrar Novo Candidato'}</h2>
          
          {erro && <div className="error-message">{erro}</div>}
          {sucesso && <div className="success-message">{sucesso}</div>}

          <form onSubmit={handleSubmit} className="candidato-form">
            <div className="form-group">
              <label htmlFor="nome">Nome completo *</label>
              <input
                type="text"
                id="nome"
                name="nome"
                value={formData.nome}
                onChange={handleInputChange}
                required
                placeholder="Digite o nome completo"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                placeholder="Digite o email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="telefone">Telefone</label>
              <input
                type="tel"
                id="telefone"
                name="telefone"
                value={formData.telefone}
                onChange={handleInputChange}
                placeholder="Digite o telefone"
              />
            </div>

            <div className="form-group">
              <label htmlFor="experiencia">Experiência Profissional</label>
              <textarea
                id="experiencia"
                name="experiencia"
                value={formData.experiencia}
                onChange={handleInputChange}
                rows="4"
                placeholder="Descreva a experiência profissional"
              />
            </div>

            <div className="form-actions">
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Salvando...' : (editando ? 'Atualizar' : 'Cadastrar')}
              </button>
              
              {editando && (
                <button type="button" onClick={cancelarEdicao} className="btn-secondary">
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="list-section">
          <h2>Candidatos Cadastrados ({candidatos.length})</h2>
          
          {loading && <div className="loading">Carregando...</div>}
          
          {candidatos.length === 0 && !loading ? (
            <div className="empty-state">Nenhum candidato cadastrado ainda.</div>
          ) : (
            <div className="candidatos-grid">
              {candidatos.map((candidato) => (
                <div key={candidato.id} className="candidato-card">
                  <div className="candidato-header">
                    <h3>{candidato.nome}</h3>
                    <span className="candidato-id">ID: {candidato.id}</span>
                  </div>
                  
                  <div className="candidato-info">
                    <p><strong>Email:</strong> {candidato.email}</p>
                    {candidato.telefone && (
                      <p><strong>Telefone:</strong> {candidato.telefone}</p>
                    )}
                    {candidato.experiencia && (
                      <div className="experiencia">
                        <strong>Experiência:</strong>
                        <p className="experiencia-text">{candidato.experiencia}</p>
                      </div>
                    )}
                    <p className="data-cadastro">
                      <strong>Cadastrado em:</strong> {new Date(candidato.data_cadastro).toLocaleString('pt-BR')}
                    </p>
                  </div>

                  <div className="candidato-actions">
                    <button 
                      onClick={() => handleEdit(candidato)}
                      className="btn-edit"
                      disabled={loading}
                    >
                      Editar
                    </button>
                    <button 
                      onClick={() => handleDelete(candidato.id, candidato.nome)}
                      className="btn-delete"
                      disabled={loading}
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;