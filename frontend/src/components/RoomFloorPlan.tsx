import type { FocusEvent } from "react";

import type { AirConditioner, Lamp } from "../types";
import { AcIcon } from "./AcIcon";
import { lampLayoutPosition } from "./lampLayout";

const MIN_AC_TEMP = 16;
const MAX_AC_TEMP = 30;

type Props = {
  lamps: Lamp[];
  airConditioners: AirConditioner[];
  disabled?: boolean;
  acDisabled?: boolean;
  canSetTemp?: boolean;
  onToggle: (lamp: Lamp) => void;
  onAcToggle: (unit: AirConditioner) => void;
  onAcTempChange: (unit: AirConditioner, temp: number) => void;
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

export function RoomFloorPlan({
  lamps,
  airConditioners,
  disabled,
  acDisabled,
  canSetTemp,
  onToggle,
  onAcToggle,
  onAcTempChange,
}: Props) {
  const sortedLamps = [...lamps].sort((a, b) => a.slot - b.slot);
  const sortedAc = [...airConditioners].sort((a, b) => a.slot - b.slot);
  const lampTotal = sortedLamps.length;
  const acTotal = sortedAc.length;
  const rowCount = Math.max(lampTotal, acTotal, 1);

  return (
    <div className="room-floor-wrap">
      <div
        className="room-floor"
        style={{ minHeight: rowCount > 4 ? `${120 + rowCount * 36}px` : undefined }}
        aria-label="Planta da sala com lâmpadas e ar-condicionado"
      >
        <div className="room-floor-label room-floor-label--back">Fundo</div>
        <div className="room-floor-label room-floor-label--front">Frente</div>

        <div className="room-ac-stack">
          {sortedAc.map((unit) => (
            <div key={unit.id} className="room-ac-control">
              <button
                type="button"
                className={`room-ac-btn ${unit.is_on ? "is-on" : "is-off"}`}
                disabled={acDisabled}
                onClick={() => onAcToggle(unit)}
                aria-pressed={unit.is_on}
                aria-label={`${unit.name}, ${unit.power_watts} watts, ${unit.target_temp_c} graus, ${unit.is_on ? "ligado" : "desligado"}. Clique para alternar.`}
              >
                <AcIcon on={unit.is_on} />
                <span className="room-ac-caption">
                  {unit.name}
                  <span className="room-ac-temp">{unit.target_temp_c}°C</span>
                  <span className="room-ac-watts">{unit.power_watts} W</span>
                </span>
              </button>
              {canSetTemp && (
                <label className="room-ac-temp-edit">
                  <span className="muted small">Ajustar °C</span>
                  <input
                    key={`${unit.id}-${unit.target_temp_c}`}
                    type="number"
                    min={MIN_AC_TEMP}
                    max={MAX_AC_TEMP}
                    defaultValue={unit.target_temp_c}
                    disabled={acDisabled}
                    onBlur={(e: FocusEvent<HTMLInputElement>) => {
                      const value = Number(e.target.value);
                      if (
                        Number.isFinite(value) &&
                        value >= MIN_AC_TEMP &&
                        value <= MAX_AC_TEMP &&
                        value !== unit.target_temp_c
                      ) {
                        onAcTempChange(unit, value);
                      }
                    }}
                  />
                </label>
              )}
            </div>
          ))}
        </div>

        {sortedLamps.map((lamp, index) => {
          const pos = lampLayoutPosition(index, lampTotal);
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
