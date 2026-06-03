/** Posição percentual na planta (frente = baixo, fundo = topo). */
export function lampLayoutPosition(index: number, total: number): { top: string; left: string } {
  if (total <= 0) return { top: "50%", left: "50%" };
  if (total === 1) return { top: "50%", left: "50%" };
  const pct = 12 + (index / (total - 1)) * 76;
  return { top: `${pct}%`, left: "50%" };
}

export const MAX_LAMPS_PER_ROOM = 12;
