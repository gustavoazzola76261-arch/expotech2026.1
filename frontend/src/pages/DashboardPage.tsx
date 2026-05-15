import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import { RoomPreviewMini } from "../components/RoomPreviewMini";
import type { Me, RoomOverview } from "../types";

async function fetchOverview(): Promise<RoomOverview[]> {
  return apiFetch<RoomOverview[]>("/api/v1/rooms/overview");
}

export function DashboardPage() {
  const qc = useQueryClient();
  const { data: me, isLoading: loadingMe } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data, isLoading, error } = useQuery({
    queryKey: ["rooms-overview"],
    queryFn: fetchOverview,
    enabled: !!me && me.role !== "professor",
    refetchInterval: 5000,
  });

  const allOff = useMutation({
    mutationFn: () => apiFetch<{ turned_off: number }>("/api/v1/lamps/all-off", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const allOn = useMutation({
    mutationFn: () => apiFetch<{ turned_on: number }>("/api/v1/lamps/all-on", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const roomOff = useMutation({
    mutationFn: (roomId: number) =>
      apiFetch<{ turned_off: number }>(`/api/v1/rooms/${roomId}/lamps/all-off`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const roomOn = useMutation({
    mutationFn: (roomId: number) =>
      apiFetch<{ turned_on: number }>(`/api/v1/rooms/${roomId}/lamps/all-on`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const canBulk = me?.role === "admin" || me?.role === "mestre";

  if (loadingMe) return <p className="muted">Carregando…</p>;

  if (me?.role === "professor") {
    if (me.room_ids.length > 0) {
      return <Navigate to={`/salas/${me.room_ids[0]}`} replace />;
    }
    return (
      <div>
        <h2>Acesso às salas</h2>
        <p className="muted">Sua conta não está vinculada a nenhuma sala. Procure o administrador do sistema.</p>
      </div>
    );
  }

  if (isLoading) return <p className="muted">Carregando salas…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;

  return (
    <div>
      <div className="dashboard-header">
        <div>
          <h2>Salas</h2>
          <p className="muted">Visualize o estado atual. Clique na sala para controlar as lâmpadas.</p>
        </div>
        {canBulk && (
          <div className="bulk-actions">
            <button type="button" className="btn-secondary" disabled={allOn.isPending} onClick={() => allOn.mutate()}>
              Ligar todas
            </button>
            <button type="button" className="btn-danger-outline" disabled={allOff.isPending} onClick={() => allOff.mutate()}>
              Desligar todas
            </button>
          </div>
        )}
      </div>

      {allOff.isSuccess && (
        <p className="muted small">Último comando global: {allOff.data?.turned_off ?? 0} lâmpada(s) desligada(s).</p>
      )}
      {allOn.isSuccess && (
        <p className="muted small">Último comando global: {allOn.data?.turned_on ?? 0} lâmpada(s) ligada(s).</p>
      )}

      <div className="room-overview-grid">
        {data?.map((room) => (
          <div key={room.id} className="card room-overview-card">
            <Link to={`/salas/${room.id}`} className="room-overview-link">
              <RoomPreviewMini lamps={room.lamps} roomName={room.name} roomCode={room.code} />
            </Link>
            <div className="room-overview-actions">
              <Link to={`/salas/${room.id}`} className="inline-link">
                Entrar na sala →
              </Link>
              {canBulk && (
                <div className="room-bulk-buttons">
                  <button
                    type="button"
                    className="btn-secondary"
                    disabled={roomOn.isPending}
                    onClick={() => roomOn.mutate(room.id)}
                  >
                    Ligar sala
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    disabled={roomOff.isPending}
                    onClick={() => roomOff.mutate(room.id)}
                  >
                    Desligar sala
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
