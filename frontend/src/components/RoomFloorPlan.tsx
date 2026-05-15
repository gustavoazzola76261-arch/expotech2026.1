import type { Lamp } from "../types";

type Props = {
  lamps: Lamp[];
  disabled?: boolean;
  onToggle: (lamp: Lamp) => void;
};

/** Posição por slot: 1 = frente (baixo), 2 = meio, 3 = fundo (topo). */
const SLOT_LAYOUT: Record<number, { top: string; left: string }> = {
  1: { top: "78%", left: "50%" },
  2: { top: "50%", left: "50%" },
  3: { top: "22%", left: "50%" },
};

function LedLampIcon({ on, uid }: { on: boolean; uid: number }) {
  const filterId = `led-glow-${uid}`;
  return (
    <svg className={`led-lamp-svg ${on ? "led-lamp-on" : "led-lamp-off"}`} viewBox="0 0 64 80" width="56" height="70" aria-hidden>
      <defs>
        <filter id={filterId} x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <g filter={on ? `url(#${filterId})` : undefined}>
        <path
          d="M32 8 C22 8 14 18 14 28 C14 38 20 44 22 52 L22 58 L42 58 L42 52 C44 44 50 38 50 28 C50 18 42 8 32 8 Z"
          className="led-bulb-glass"
        />
        <rect x="20" y="58" width="24" height="8" rx="2" className="led-bulb-base" />
        <path d="M26 20 L30 28 L34 20" className="led-filament" fill="none" strokeWidth="2" strokeLinecap="round" />
        <path d="M30 28 L30 36" className="led-filament" fill="none" strokeWidth="2" strokeLinecap="round" />
      </g>
    </svg>
  );
}

export function RoomFloorPlan({ lamps, disabled, onToggle }: Props) {
  const sorted = [...lamps].sort((a, b) => a.slot - b.slot);

  return (
    <div className="room-floor-wrap">
      <div className="room-floor" aria-label="Planta da sala com lâmpadas LED">
        <div className="room-floor-label room-floor-label--back">Fundo</div>
        <div className="room-floor-label room-floor-label--front">Frente</div>

        {sorted.map((lamp) => {
          const pos = SLOT_LAYOUT[lamp.slot] ?? SLOT_LAYOUT[2];
          return (
            <button
              key={lamp.id}
              type="button"
              className={`room-lamp-btn ${lamp.is_on ? "is-on" : "is-off"}`}
              style={{ top: pos.top, left: pos.left }}
              disabled={disabled}
              onClick={() => onToggle(lamp)}
              aria-pressed={lamp.is_on}
              aria-label={`${lamp.name}, ${lamp.power_watts} watts, ${lamp.is_on ? "ligada" : "desligada"}. Clique para alternar.`}
            >
              <LedLampIcon on={lamp.is_on} uid={lamp.id} />
              <span className="room-lamp-caption">
                {lamp.name}
                <span className="room-lamp-watts">{lamp.power_watts} W</span>
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
