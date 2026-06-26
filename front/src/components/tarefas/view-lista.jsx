import { StatusBadge, Badge } from '../ui/badge'
import { Calendar, Clock } from 'lucide-react'

export function ViewLista({ tarefas, onEdit }) {
  return (
    <div className="border border-white/10 rounded-2xl overflow-hidden">
      <table className="w-full text-sm" role="grid">
        <thead>
          <tr className="border-b border-white/5 text-left text-xs text-zinc-400 uppercase tracking-wider">
            <th className="p-4 font-medium">Tarefa</th>
            <th className="p-4 font-medium hidden sm:table-cell">Etapa</th>
            <th className="p-4 font-medium hidden md:table-cell">Esforço</th>
            <th className="p-4 font-medium hidden md:table-cell">Áreas da vida</th>
            <th className="p-4 font-medium hidden lg:table-cell">Prazo</th>
          </tr>
        </thead>
        <tbody>
          {tarefas.map((t) => (
            <tr
              key={t.id}
              className="border-b border-white/5 hover:bg-white/5 cursor-pointer transition-colors"
              onClick={() => onEdit(t)}
              tabIndex={0}
              role="row"
              aria-label={`Editar tarefa: ${t.nome}`}
              onKeyDown={(e) => { if (e.key === 'Enter') onEdit(t) }}
            >
              <td className="p-4 text-white font-medium">{t.nome}</td>
              <td className="p-4 hidden sm:table-cell">
                <StatusBadge status={t.status} />
              </td>
              <td className="p-4 hidden md:table-cell">
                {t.duracao && (
                  <Badge className="bg-zinc-800 text-zinc-300 border-zinc-700/50">
                    <Clock size={12} className="mr-1" />
                    {t.duracao}
                  </Badge>
                )}
              </td>
              <td className="p-4 hidden md:table-cell text-zinc-400 text-xs">
                {t.areas_nomes?.join(', ') || '—'}
              </td>
              <td className="p-4 hidden lg:table-cell text-zinc-500 text-xs">
                {t.prazo ? (
                  <span className="flex items-center gap-1">
                    <Calendar size={12} />
                    {new Date(t.prazo).toLocaleDateString('pt-BR')}
                  </span>
                ) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
