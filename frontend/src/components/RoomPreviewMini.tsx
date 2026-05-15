import type { Lamp } from "../types";

const SLOT_POS: Record<number, { top: string; left: string }> = {
  1: { top: "72%", left: "50%" },
  2: { top: "50%", left: "50%" },
  3: { top: "28%", left: "50%" },
};

type Props = {
  lamps: Lamp[];
  roomName: string;
  roomCode: string;
};

export function RoomPreviewMini({ lamps, roomName, roomCode }: Props) {
  const sorted = [...lamps].sort((a, b) => a.slot - b.slot);

  return (
    <div className="room-preview-mini">
      <div className="room-preview-floor" aria-hidden>
        {sorted.map((lamp) => {
          const pos = SLOT_POS[lamp.slot] ?? SLOT_POS[2];
          return (
            <span
              key={lamp.id}
              className={`room-preview-dot ${lamp.is_on ? "on" : "off"}`}
              style={{ top: pos.top, left: pos.left }}
              title={`${lamp.name}: ${lamp.is_on ? "ligada" : "desligada"}`}
            />
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
