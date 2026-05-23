import type { AirConditioner, Lamp } from "../types";
import { acLayoutPosition } from "./acLayout";
import { AcIcon } from "./AcIcon";
import { lampLayoutPosition } from "./lampLayout";

type Props = {
  lamps: Lamp[];
  airConditioners?: AirConditioner[];
  roomName: string;
  roomCode: string;
};

export function RoomPreviewMini({ lamps, airConditioners = [], roomName, roomCode }: Props) {
  const sortedLamps = [...lamps].sort((a, b) => a.slot - b.slot);
  const sortedAc = [...airConditioners].sort((a, b) => a.slot - b.slot);
  const lampTotal = sortedLamps.length;
  const acTotal = sortedAc.length;
  const rowCount = Math.max(lampTotal, acTotal, 1);

  return (
    <div className="room-preview-mini">
      <div
        className="room-preview-floor"
        style={{ minHeight: rowCount > 3 ? `${56 + rowCount * 10}px` : undefined }}
        aria-hidden
      >
        {sortedLamps.map((lamp, index) => {
          const pos = lampLayoutPosition(index, lampTotal);
          return (
            <span
              key={lamp.id}
              className={`room-preview-dot ${lamp.is_on ? "on" : "off"}`}
              style={{ top: pos.top, left: pos.left }}
              title={`${lamp.name}: ${lamp.is_on ? "ligada" : "desligada"}`}
            />
          );
        })}
        {sortedAc.map((unit, index) => {
          const pos = acLayoutPosition(index, acTotal);
          return (
            <span
              key={unit.id}
              className={`room-preview-ac ${unit.is_on ? "on" : "off"}`}
              style={{ top: pos.top, right: pos.right }}
              title={`${unit.name}: ${unit.is_on ? "ligado" : "desligado"}, ${unit.target_temp_c}°C`}
            >
              <AcIcon on={unit.is_on} />
            </span>
          );
        })}
      </div>
      <div className="room-preview-caption">
        <strong>{roomName}</strong>
        <span className="muted small">{roomCode}</span>
      </div>
    </div>
  );
}
