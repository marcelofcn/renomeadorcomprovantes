import { useEffect, useState } from 'react'
import axios from 'axios'

type Comprovante = {
  id: number; bank: string; account: string; date: string; amount: number;
  description: string; type: string; saved_filename: string;
  dest_bank?: string; dest_account?: string;
}

type GrupoPagamento = {
  key: string; bank: string; account: string; date: string; totalAmount: number; count: number;
}

// 1. MAPEAMENTO UNIFICADO - Centralizado e completo
const UNIDADES_MAP: { [key: string]: string } = {
    // FILIAIS SICREDI
    "331049": "Aracaju (Sicredi 33104-9)",
    "331474": "Brasília (Sicredi 33147-4)",
    "331395": "São Paulo (Sicredi 33139-5)",
    "748280": "Várzea Grande (Sicredi 74828-0)",
    "255208": "Loja CB (Sicredi 25520-8)",
    "25520":  "Loja CB (Sicredi 25520-0)", 
    "282035": "Matriz (Sicredi 28203-5)",
    "28203":  "Matriz (Sicredi 28203-0)", 
    "697239": "Alimentação (Sicredi 69723-9)",

    // MATRIZ E FILIAIS BB
    "9319X":  "Matriz (BB 9319-X)",
    "93190":  "Matriz (BB 9319-X)", 
    "73741":  "PIX Revenda (BB 7374-1)",
    "70114":  "Vitoria da Conquista (BB 7011-4)",

    // BRADESCO
    "92207":  "Matriz (Bradesco 9220-7)",
    "9220":   "Matriz (Bradesco 9220-7)"
};

// 2. FUNÇÃO DE TRADUÇÃO INTELIGENTE (Mantida fora para ser global)
const traduzirUnidade = (contaRaw: string | undefined) => {
    if (!contaRaw) return "---";
    
    // Remove pontos e traços, preserva o X
    let limpa = contaRaw.toUpperCase().replace(/[^0-9X]/g, '');
    
    // Tratamento para Banco do Brasil (X que virou 0)
    if (limpa.endsWith('0') && UNIDADES_MAP[limpa.slice(0, -1) + 'X']) {
        return UNIDADES_MAP[limpa.slice(0, -1) + 'X'];
    }
    
    const limpaSemZero = limpa.replace(/^0+/, '');
    return UNIDADES_MAP[limpa] || UNIDADES_MAP[limpaSemZero] || contaRaw;
};

function Dashboard() {
  const [dados, setDados] = useState<Comprovante[]>([])
  const [loading, setLoading] = useState(true)

  // Estados dos Filtros (Todos vazios para vir tudo primeiro)
  const [filtroModo, setFiltroModo] = useState('PAGAMENTOS')
  const [filtroBanco, setFiltroBanco] = useState('')
  const [filtroConta, setFiltroConta] = useState('')
  const [filtroAno, setFiltroAno] = useState('') 
  const [filtroMes, setFiltroMes] = useState('')
  const [filtroDia, setFiltroDia] = useState('')

  useEffect(() => {
    axios.get('/api/comprovantes').then(res => {
      setDados(res.data.comprovantes || [])
      setLoading(false)
    })
  }, [])

  const formatarBanco = (nome: string) => {
      if (nome.includes("BRASIL")) return "BB";
      if (nome.includes("SICREDI")) return "Sicredi";
      return nome.replace('_', ' ');
  }

  // Gera lista de contas disponíveis para o seletor
  const contasDisponiveis = Array.from(new Set(
    dados
      .filter(d => filtroBanco === '' || d.bank === filtroBanco)
      .map(d => d.account)
  )).sort();

  // 3. APLICAÇÃO DOS FILTROS
  const dadosFiltrados = dados.filter(item => {
    const [ano, mes, dia] = item.date.split('-')
    const bateBanco = filtroBanco === '' || item.bank === filtroBanco
    const bateConta = filtroConta === '' || item.account === filtroConta
    const bateAno = filtroAno === '' || ano === filtroAno
    const bateMes = filtroMes === '' || mes === filtroMes
    const bateDia = filtroDia === '' || dia === filtroDia
    const bateModo = filtroModo === 'TRANSFERENCIAS' 
        ? item.type === 'TRANSFERENCIA_INTERNA' 
        : item.type !== 'TRANSFERENCIA_INTERNA'
    
    return bateBanco && bateConta && bateAno && bateMes && bateDia && bateModo
  })

  // 4. AGRUPAMENTO PARA CARDS
  const pagamentosAgrupados = filtroModo === 'PAGAMENTOS' ? dadosFiltrados.reduce((acc: GrupoPagamento[], curr) => {
    const key = `${curr.date}|${curr.bank}|${curr.account}`
    const existente = acc.find(g => g.key === key)
    if (existente) {
      existente.totalAmount += curr.amount
      existente.count += 1
    } else {
      acc.push({
        key, bank: curr.bank, account: curr.account, date: curr.date,
        totalAmount: curr.amount, count: 1
      })
    }
    return acc
  }, []) : []

  const totalGeral = dadosFiltrados.reduce((sum, item) => sum + (item.amount || 0), 0);

  return (
    <div className="page-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Dashboard Financeiro</h1>
        <div style={{ background: '#e0e0e0', padding: '5px', borderRadius: '10px', display: 'flex', gap: '5px' }}>
            <button onClick={() => setFiltroModo('PAGAMENTOS')} style={{ ...tabButtonStyle, background: filtroModo === 'PAGAMENTOS' ? '#fff' : 'transparent', fontWeight: filtroModo === 'PAGAMENTOS' ? 'bold' : 'normal' }}>Pagamentos</button>
            <button onClick={() => setFiltroModo('TRANSFERENCIAS')} style={{ ...tabButtonStyle, background: filtroModo === 'TRANSFERENCIAS' ? '#fff' : 'transparent', fontWeight: filtroModo === 'TRANSFERENCIAS' ? 'bold' : 'normal' }}>Transferências</button>
        </div>
      </div>
      
      <div style={filterBarStyle}>
        <div style={filterGroupStyle}><label style={labelStyle}>Banco</label>
          <select value={filtroBanco} onChange={e => { setFiltroBanco(e.target.value); setFiltroConta('') }} style={selectStyle}>
            <option value="">Todos</option>
            <option value="SICREDI">Sicredi</option>
            <option value="BRADESCO">Bradesco</option>
            <option value="BANCO_DO_BRASIL">Banco do Brasil</option>
          </select>
        </div>

        <div style={filterGroupStyle}><label style={labelStyle}>Unidade (Conta)</label>
          <select value={filtroConta} onChange={e => setFiltroConta(e.target.value)} style={selectStyle}>
            <option value="">Todas</option>
            {contasDisponiveis.map(c => <option key={c} value={c}>{traduzirUnidade(c)}</option>)}
          </select>
        </div>

        <div style={filterGroupStyle}><label style={labelStyle}>Ano</label>
          <select value={filtroAno} onChange={e => setFiltroAno(e.target.value)} style={selectStyle}>
            <option value="">Todos</option><option value="2025">2025</option><option value="2026">2026</option>
          </select>
        </div>

        <div style={filterGroupStyle}><label style={labelStyle}>Mês</label>
          <select value={filtroMes} onChange={e => setFiltroMes(e.target.value)} style={selectStyle}>
            <option value="">Todos</option>
            {['01','02','03','04','05','06','07','08','09','10','11','12'].map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>

        <div style={filterGroupStyle}><label style={labelStyle}>Dia</label>
          <select value={filtroDia} onChange={e => setFiltroDia(e.target.value)} style={selectStyle}>
            <option value="">Todos</option>
            {Array.from({length: 31}, (_, i) => (i+1).toString().padStart(2, '0')).map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>

        <button onClick={() => { setFiltroBanco(''); setFiltroConta(''); setFiltroAno(''); setFiltroMes(''); setFiltroDia('') }} style={clearButtonStyle}>Limpar</button>
      </div>

      <div style={{ marginBottom: '20px', padding: '10px 20px', background: '#e3f2fd', borderRadius: '8px', display: 'inline-block', border: '1px solid #bbdefb' }}>
          <strong>Soma do Período:</strong> R$ {totalGeral.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
      </div>

      {filtroModo === 'PAGAMENTOS' ? (
        <div style={gridStyle}>
          {pagamentosAgrupados.map((g) => (
            <div key={g.key} style={cardStyle}>
              <div style={{display:'flex', justifyContent:'space-between'}}>
                <span style={getBadgeStyle(g.bank)}>{formatarBanco(g.bank)}</span>
                <span style={{fontSize:'0.8rem', color:'#888'}}>{g.date.split('-').reverse().join('/')}</span>
              </div>
              <div style={{margin:'15px 0 5px 0', fontSize:'1rem', color:'#333'}}><strong>{traduzirUnidade(g.account)}</strong></div>
              <p style={{margin:'0', color:'#666', fontSize:'0.85rem'}}>{g.count} arquivos processados</p>
              <div style={valorStyle}>R$ {g.totalAmount.toLocaleString('pt-BR', {minimumFractionDigits:2})}</div>
              <button onClick={() => window.open(`/api/download/zip/${g.date}/${g.account}`)} className="btn-primary" style={{width:'100%', marginTop:'10px'}}>Baixar ZIP</button>
            </div>
          ))}
        </div>
      ) : (
        <div style={tableContainerStyle}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f8f9fa', textAlign: 'left', borderBottom: '2px solid #eee' }}>
                <th style={thStyle}>Data</th>
                <th style={thStyle}>Origem (Unidade)</th>
                <th style={thStyle}>Destino (Unidade)</th>
                <th style={thStyle}>Valor</th>
                <th style={thStyle}>Ação</th>
              </tr>
            </thead>
            <tbody>
              {dadosFiltrados.map(t => (
                <tr key={t.id} style={{ borderBottom: '1px solid #f1f1f1' }}>
                  <td style={tdStyle}>{t.date.split('-').reverse().join('/')}</td>
                  <td style={tdStyle}><strong>{formatarBanco(t.bank)}</strong> - {traduzirUnidade(t.account)}</td>
                  <td style={{ ...tdStyle, color: '#004a80', fontWeight: 'bold' }}>{traduzirUnidade(t.dest_account)}</td>
                  <td style={tdStyle}><strong>R$ {t.amount.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</strong></td>
                  <td style={tdStyle}><button onClick={() => window.open(`/api/download/${t.saved_filename}`, '_blank')} style={{cursor:'pointer', padding:'2px 8px'}}>Ver</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// Estilos
const tabButtonStyle = { border: 'none', padding: '8px 20px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.9rem' }
const filterBarStyle = { display: 'flex', gap: '15px', background: '#f1f4f9', padding: '15px', borderRadius: '12px', marginBottom: '25px', alignItems: 'flex-end', flexWrap: 'wrap' as any }
const filterGroupStyle = { display: 'flex', flexDirection: 'column' as any, gap: '4px' }
const labelStyle = { fontSize: '0.65rem', fontWeight: 'bold', color: '#666', textTransform: 'uppercase' as any }
const selectStyle = { padding: '8px', borderRadius: '6px', border: '1px solid #ccc', minWidth: '130px', backgroundColor: '#fff' }
const clearButtonStyle = { border: 'none', background: 'none', color: '#d32f2f', cursor: 'pointer', textDecoration: 'underline', fontSize: '0.8rem' }
const cardStyle = { background: '#fff', border: '1px solid #e0e0e0', borderRadius: '12px', padding: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }
const gridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }
const tableContainerStyle = { background: '#fff', borderRadius: '12px', border: '1px solid #eee', overflow: 'hidden' }
const thStyle = { padding: '12px', fontSize: '0.8rem', color: '#666' }
const tdStyle = { padding: '12px', fontSize: '0.85rem' }
const valorStyle = { fontSize: '1.35rem', fontWeight: 'bold', color: '#2e7d32', margin: '12px 0' }

const getBadgeStyle = (bank: string) => {
  let colors = { bg: '#e3f2fd', text: '#1976d2' };
  if (bank === 'BRADESCO') colors = { bg: '#ffebee', text: '#c62828' };
  if (bank === 'BANCO_DO_BRASIL') colors = { bg: '#fff9c4', text: '#f57f17' };
  return { background: colors.bg, color: colors.text, padding: '2px 8px', borderRadius: '10px', fontSize: '0.65rem', fontWeight: 'bold' as any }
}

export default Dashboard