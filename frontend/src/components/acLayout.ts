/** Posição dos aparelhos de ar na miniatura (lado direito da planta). */
export function acLayoutPosition(index: number, total: number): { top: string; right: string } {
  if (total <= 0) return { top: "50%", right: "8%" };
  if (total === 1) return { top: "22%", right: "8%" };
  const pct = 14 + (index / (total - 1)) * 56;
  return { top: `${pct}%`, right: "6%" };
}

export const MAX_AC_UNITS_PER_ROOM = 4;
