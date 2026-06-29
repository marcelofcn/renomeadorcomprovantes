import { FormEvent, useState, type ChangeEvent, useEffect } from 'react'
import api from '../services/api'

type ProcessedFile = {
  id: number
  saved_filename: string
  description: string
  bank: string
  comprovante_type: string
  amount: number
  date: string
  path: string
}

function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [banco, setBanco] = useState<string>('SICREDI') // Estado para o banco selecionado
  const [message, setMessage] = useState<string>('Selecione o banco e o arquivo PDF.')
  const [loading, setLoading] = useState(false)
  const [processedFiles, setProcessedFiles] = useState<ProcessedFile[]>([])
  const [lastSavedFilename, setLastSavedFilename] = useState<string>('')

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null
    setFile(selectedFile)
    if (selectedFile) {
      setMessage(`Arquivo pronto: ${selectedFile.name}`)
    }
  }

  const carregarComprovantes = async () => {
    try {
      const response = await api.listarComprovantes()
      setProcessedFiles(response.data.comprovantes || [])
    } catch (error) {
      console.error("Erro ao carregar lista:", error)
    }
  }

  useEffect(() => {
    carregarComprovantes()
  }, [])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!file) {
      setMessage('Por favor, selecione um arquivo antes de enviar.')
      return
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('bank', banco) // Envia o banco escolhido para o Backend (campo 'bank')

    try {
      setLoading(true)
      setMessage('Processando comprovantes... aguarde.')
      
      const response = await api.uploadComprovante(formData)
      
      // O backend agora retorna uma mensagem detalhada com sucessos/erros/travas
      setMessage(response.data.message || 'Upload realizado com sucesso.')
      
      if (response.data.data?.detalhes?.[0]) {
        setLastSavedFilename(response.data.data.detalhes[0])
      }
      
      await carregarComprovantes()
    } catch (error: any) {
      console.error("Erro no upload:", error)
      // Captura a mensagem da trava de segurança do backend
      const errorMsg = error.response?.data?.detail || 'Falha no upload. Verifique o backend.'
      setMessage(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // Função auxiliar para definir a cor do badge por banco
  const getBadgeColor = (bank: string) => {
    switch (bank) {
      case 'BRADESCO': return { bg: '#ffebee', text: '#c62828' };
      case 'BANCO_DO_BRASIL': return { bg: '#fff9c4', text: '#f57f17' };
      case 'SICREDI': return { bg: '#e3f2fd', text: '#1976d2' };
      default: return { bg: '#f5f5f5', text: '#666' };
    }
  }

  return (
    <div className="page-card">
      <h1>Upload de Comprovante</h1>
      <p>Selecione o banco de origem e envie o PDF para renomeação automática.</p>

      <form onSubmit={handleSubmit} className="upload-form">
        {/* SELETOR DE BANCO */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#444' }}>
            1. Selecione o Banco:
          </label>
          <select 
            value={banco} 
            onChange={(e) => setBanco(e.target.value)}
            style={{ 
              width: '100%', 
              padding: '12px', 
              borderRadius: '8px', 
              border: '1px solid #ccc',
              fontSize: '1rem',
              backgroundColor: '#fff',
              cursor: 'pointer'
            }}
          >
            <option value="SICREDI">Sicredi</option>
            <option value="BRADESCO">Bradesco</option>
            <option value="BANCO_DO_BRASIL">Banco do Brasil</option>
          </select>
        </div>

        {/* SELETOR DE ARQUIVO */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#444' }}>
            2. Escolha o PDF:
          </label>
          <label className="file-label">
            <input type="file" accept="application/pdf" onChange={handleFileChange} />
            {file ? '📄 ' + file.name : '📁 Selecionar arquivo PDF'}
          </label>
        </div>

        <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%' }}>
          {loading ? '⚙️ Processando Páginas...' : '🚀 Enviar e Renomear'}
        </button>
      </form>

      {/* MENSAGEM DE STATUS */}
      <div 
        className="upload-note" 
        style={{ 
          marginTop: '20px', 
          backgroundColor: message.includes('Erro') || message.includes('Falha') ? '#ffebee' : '#f1f4f9',
          color: message.includes('Erro') || message.includes('Falha') ? '#c62828' : '#333',
          borderLeft: message.includes('Erro') || message.includes('Falha') ? '4px solid #c62828' : '4px solid #004a80'
        }}
      >
        <strong>Status:</strong> {message}
      </div>

      {/* FEEDBACK DO ÚLTIMO ARQUIVO */}
      {lastSavedFilename && (
        <div className="upload-note success" style={{ borderLeft: '4px solid #2e7d32', backgroundColor: '#e8f5e9' }}>
          <strong>Salvo com sucesso:</strong>{' '}
          <a href={`/api/download/${encodeURIComponent(lastSavedFilename)}`} target="_blank" rel="noreferrer" style={{ color: '#2e7d32', fontWeight: 'bold' }}>
            {lastSavedFilename}
          </a>
        </div>
      )}

      {/* LISTA DE RECENTES */}
      <div className="upload-note" style={{ marginTop: '30px' }}>
        <h2 style={{ fontSize: '1.1rem', marginBottom: '15px', borderBottom: '1px solid #ddd', paddingBottom: '5px' }}>
          Processados Recentemente:
        </h2>
        {processedFiles.length === 0 ? (
          <div style={{ color: '#999', textAlign: 'center', padding: '20px' }}>Nenhum comprovante na lista.</div>
        ) : (
          <ul style={{ marginTop: 8, paddingLeft: 0, listStyleType: 'none' }}>
            {processedFiles.map((item) => {
              const colors = getBadgeColor(item.bank);
              return (
                <li key={item.id} style={{ 
                  marginBottom: '12px', 
                  padding: '10px', 
                  backgroundColor: '#fff', 
                  borderRadius: '8px', 
                  border: '1px solid #eee',
                  fontSize: '0.9rem' 
                }}>
                  <span style={{ 
                    fontSize: '0.65rem', 
                    background: colors.bg,
                    color: colors.text,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    marginRight: '10px',
                    fontWeight: 'bold',
                    display: 'inline-block',
                    verticalAlign: 'middle'
                  }}>
                    {item.bank.replace('_', ' ')}
                  </span>
                  <a href={`/api/download/${encodeURIComponent(item.saved_filename)}`} target="_blank" rel="noreferrer" style={{ textDecoration: 'none', color: '#004a80', fontWeight: '500' }}>
                    {item.saved_filename}
                  </a>
                  <div style={{ color: '#666', marginTop: '4px', marginLeft: '0' }}>
                    <small>
                      {item.description} — <strong>R$ {(item.amount ?? 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong>
                    </small>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  )
}

export default Upload