/**
 * API client para o backend Django (CONTRATOS.md §2).
 *
 * Em uso normal, toda leitura/escrita passa pela API Django, que usa o Notion
 * como fonte de verdade. O mock só é usado quando VITE_MOCK_API=true.
 */

const USE_MOCK = import.meta.env.VITE_MOCK_API === 'true'

// ─── Mock data (contrato §1) ────────────────────────────────────────────

const MOCK_OPCOES = {
  status: [
    '00. Inbox',
    '01. Priorizadas',
    '02. ASAP',
    '03. Fazendo',
    '04. Esperando',
    '05. Adiadas',
    '06. Feito',
  ],
  duracao: ['Minutos', 'Poucas horas', 'Dias', 'Semanas', 'Meses'],
  areas: [
    { id: 'area-1', nome: 'Estudos' },
    { id: 'area-2', nome: 'Trabalho' },
    { id: 'area-3', nome: 'Saude' },
    { id: 'area-4', nome: 'Projetos' },
  ],
}

let mockIdCounter = 7

const MOCK_TAREFAS = [
  {
    id: 'mock-1',
    nome: 'Estudar a API do Notion',
    status: '03. Fazendo',
    prazo: '2026-07-01',
    duracao: 'Dias',
    areas: ['area-1'],
    areas_nomes: ['Estudos'],
    url: null,
  },
  {
    id: 'mock-2',
    nome: 'Configurar CI/CD do repositorio',
    status: '00. Inbox',
    prazo: null,
    duracao: 'Poucas horas',
    areas: ['area-4'],
    areas_nomes: ['Projetos'],
    url: null,
  },
  {
    id: 'mock-3',
    nome: 'Revisar PR do front React',
    status: '02. ASAP',
    prazo: '2026-06-28',
    duracao: 'Minutos',
    areas: ['area-2'],
    areas_nomes: ['Trabalho'],
    url: null,
  },
  {
    id: 'mock-4',
    nome: 'Treino de forca',
    status: '01. Priorizadas',
    prazo: null,
    duracao: 'Poucas horas',
    areas: ['area-3'],
    areas_nomes: ['Saude'],
    url: null,
  },
  {
    id: 'mock-5',
    nome: 'Escrever documentacao do CLI',
    status: '04. Esperando',
    prazo: '2026-07-10',
    duracao: 'Dias',
    areas: ['area-4', 'area-1'],
    areas_nomes: ['Projetos', 'Estudos'],
    url: null,
  },
  {
    id: 'mock-6',
    nome: 'Organizar notas do semestre',
    status: '06. Feito',
    prazo: '2026-06-20',
    duracao: 'Semanas',
    areas: ['area-1'],
    areas_nomes: ['Estudos'],
    url: null,
  },
]

// ─── Helpers ─────────────────────────────────────────────────────────────

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(path, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
  } catch (error) {
    const apiError = new Error('Backend indisponivel.')
    apiError.cause = error
    throw apiError
  }
  const data = await res.json()
  if (!res.ok) {
    const msg = data?.erro?.mensagem ?? `Erro ${res.status}`
    const error = new Error(msg)
    error.status = res.status
    throw error
  }
  return data
}

// ─── Mock implementations ────────────────────────────────────────────────

const mockApi = {
  async listarTarefas(filtros = {}) {
    await delay(300)
    let list = [...MOCK_TAREFAS]
    if (filtros.status) list = list.filter((t) => t.status === filtros.status)
    if (filtros.duracao) list = list.filter((t) => t.duracao === filtros.duracao)
    if (filtros.area) list = list.filter((t) => (t.areas ?? []).includes(filtros.area))
    return { tarefas: list }
  },

  async criarTarefa(body) {
    await delay(400)
    const tarefa = {
      id: `mock-${++mockIdCounter}`,
      nome: body.nome,
      status: body.status ?? '00. Inbox',
      prazo: body.prazo ?? null,
      duracao: body.duracao ?? null,
      areas: body.areas ?? [],
      areas_nomes: (body.areas ?? []).map(
        (id) => MOCK_OPCOES.areas.find((a) => a.id === id)?.nome ?? id,
      ),
      url: null,
    }
    MOCK_TAREFAS.push(tarefa)
    return tarefa
  },

  async editarTarefa(id, body) {
    await delay(300)
    const idx = MOCK_TAREFAS.findIndex((t) => t.id === id)
    if (idx === -1) throw new Error('Tarefa nao encontrada')
    const tarefa = { ...MOCK_TAREFAS[idx], ...body }
    if (body.areas) {
      tarefa.areas_nomes = body.areas.map(
        (aid) => MOCK_OPCOES.areas.find((a) => a.id === aid)?.nome ?? aid,
      )
    }
    MOCK_TAREFAS[idx] = tarefa
    return tarefa
  },

  async opcoes() {
    await delay(200)
    return MOCK_OPCOES
  },
}

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms))
}

// ─── Real API ────────────────────────────────────────────────────────────

const realApi = {
  async listarTarefas(filtros = {}) {
    const qs = new URLSearchParams()
    if (filtros.status) qs.set('status', filtros.status)
    if (filtros.duracao) qs.set('duracao', filtros.duracao)
    if (filtros.area) qs.set('area', filtros.area)
    const query = qs.toString()
    return request(`/api/tarefas${query ? `?${query}` : ''}`)
  },

  async criarTarefa(body) {
    return request('/api/tarefas', {
      method: 'POST',
      body: JSON.stringify(body),
    })
  },

  async editarTarefa(id, body) {
    return request(`/api/tarefas/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    })
  },

  async opcoes() {
    return request('/api/opcoes')
  },
}

// ─── Exported API (mock explícito) ────────────────────────────────────────

function escolherApi(fn, mockFn) {
  return USE_MOCK ? mockFn : fn
}

export const api = {
  listarTarefas: escolherApi(realApi.listarTarefas, mockApi.listarTarefas),
  criarTarefa: escolherApi(realApi.criarTarefa, mockApi.criarTarefa),
  editarTarefa: escolherApi(realApi.editarTarefa, mockApi.editarTarefa),
  opcoes: escolherApi(realApi.opcoes, mockApi.opcoes),
}
