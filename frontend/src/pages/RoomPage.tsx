import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { apiFetch } from "../api/client";
import { RoomFloorPlan } from "../components/RoomFloorPlan";
import type { Lamp, Me, Room } from "../types";

async function fetchLamps(roomId: string): Promise<Lamp[]> {
  return apiFetch<Lamp[]>(`/api/v1/rooms/${roomId}/lamps`);
}

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

export function RoomPage() {
  const { roomId } = useParams();
  const qc = useQueryClient();
  const id = roomId ?? "";

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data: rooms } = useQuery({ queryKey: ["rooms"], queryFn: fetchRooms });
  const { data, isLoading, error } = useQuery({
    queryKey: ["lamps", id],
    queryFn: () => fetchLamps(id),
    enabled: Boolean(id),
  });

  const mutation = useMutation({
    mutationFn: async ({ lampId, action }: { lampId: number; action: "on" | "off" }) => {
      return apiFetch<Lamp>(`/api/v1/lamps/${lampId}/command`, {
        method: "POST",
        json: { action },
      });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lamps", id] }),
  });

  const roomTitle = rooms?.find((r) => String(r.id) === id)?.name;

  function toggleLamp(lamp: Lamp) {
    const action = lamp.is_on ? "off" : "on";
    mutation.mutate({ lampId: lamp.id, action });
  }

  if (!id) return null;
  if (isLoading) return <p className="muted">Carregando lâmpadas…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;

  return (
    <div className="room-page">
      {me?.role !== "professor" && (
        <Link to="/" className="back-link">
          ← Voltar às salas
        </Link>
      )}
      <h2>{roomTitle ?? `Sala #${id}`}</h2>
      <p className="muted room-page-hint">Clique em uma lâmpada para ligar ou desligar.</p>

      {data && data.length > 0 ? (
        <RoomFloorPlan lamps={data} disabled={mutation.isPending} onToggle={toggleLamp} />
      ) : (
        <p className="muted">Nenhuma lâmpada cadastrada nesta sala.</p>
      )}
    </div>
  );
}
