const STATUS_COLORS = {
  '00. Inbox': 'bg-zinc-500/10 text-zinc-300 border-zinc-500/20',
  '01. Priorizadas': 'bg-yellow-500/10 text-yellow-300 border-yellow-500/20',
  '02. ASAP': 'bg-red-500/10 text-red-300 border-red-500/20',
  '03. Fazendo': 'bg-blue-500/10 text-blue-300 border-blue-500/20',
  '04. Esperando': 'bg-orange-500/10 text-orange-300 border-orange-500/20',
  '05. Adiadas': 'bg-purple-500/10 text-purple-300 border-purple-500/20',
  '06. Feito': 'bg-green-500/10 text-green-300 border-green-500/20',
}

const STATUS_DOTS = {
  '00. Inbox': 'bg-zinc-400',
  '01. Priorizadas': 'bg-yellow-400',
  '02. ASAP': 'bg-red-400',
  '03. Fazendo': 'bg-blue-400',
  '04. Esperando': 'bg-orange-400',
  '05. Adiadas': 'bg-purple-400',
  '06. Feito': 'bg-green-400',
}

export function statusColor(status) {
  if (!status) return 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'
  return (
    STATUS_COLORS[status] ??
    'bg-brand-500/10 text-brand-400 border-brand-500/20'
  )
}

export function statusDotColor(status) {
  if (!status) return 'bg-zinc-500'
  return STATUS_DOTS[status] ?? 'bg-brand-400'
}
