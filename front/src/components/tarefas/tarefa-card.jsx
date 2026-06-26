import { Card, CardContent } from '../ui/card'
import { StatusBadge, Badge } from '../ui/badge'
import { Calendar, Clock, Layers } from 'lucide-react'

export function TarefaCard({ tarefa, onEdit }) {
  return (
    <Card
      className="cursor-pointer hover:border-brand-500/30"
      onClick={() => onEdit(tarefa)}
      role="button"
      tabIndex={0}
      aria-label={`Editar tarefa: ${tarefa.nome}`}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onEdit(tarefa) } }}
    >
      <CardContent className="space-y-3">
        <h3 className="text-sm font-semibold text-white leading-tight">
          {tarefa.nome}
        </h3>

        <div className="flex flex-wrap gap-2">
          <StatusBadge status={tarefa.status} />
          {tarefa.duracao && (
            <Badge className="bg-zinc-800 text-zinc-300 border-zinc-700/50">
              <Clock size={12} className="mr-1" />
              {tarefa.duracao}
            </Badge>
          )}
        </div>

        {tarefa.areas_nomes?.length > 0 && (
          <div className="flex items-center gap-1 text-xs text-zinc-400">
            <Layers size={12} />
            {tarefa.areas_nomes.join(', ')}
          </div>
        )}

        {tarefa.prazo && (
          <div className="flex items-center gap-1 text-xs text-zinc-500">
            <Calendar size={12} />
            {new Date(tarefa.prazo).toLocaleDateString('pt-BR')}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
