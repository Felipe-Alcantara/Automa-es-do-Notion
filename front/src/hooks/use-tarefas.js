import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'

export function useTarefas() {
  const [tarefas, setTarefas] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState(null)

  const carregar = useCallback(async () => {
    setCarregando(true)
    setErro(null)
    try {
      const data = await api.listarTarefas()
      setTarefas(data.tarefas)
    } catch (e) {
      setErro(e.message)
    } finally {
      setCarregando(false)
    }
  }, [])

  useEffect(() => { carregar() }, [carregar])

  const criar = useCallback(async (body) => {
    const tarefa = await api.criarTarefa(body)
    setTarefas((prev) => [...prev, tarefa])
    return tarefa
  }, [])

  const editar = useCallback(async (id, body) => {
    const tarefa = await api.editarTarefa(id, body)
    setTarefas((prev) => prev.map((t) => (t.id === id ? tarefa : t)))
    return tarefa
  }, [])

  return { tarefas, carregando, erro, carregar, criar, editar }
}
