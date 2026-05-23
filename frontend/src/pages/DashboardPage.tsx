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

  const allLampsOff = useMutation({
    mutationFn: () => apiFetch<{ turned_off: number }>("/api/v1/lamps/all-off", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const allLampsOn = useMutation({
    mutationFn: () => apiFetch<{ turned_on: number }>("/api/v1/lamps/all-on", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const allAcOff = useMutation({
    mutationFn: () => apiFetch<{ turned_off: number }>("/api/v1/ac/all-off", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const allAcOn = useMutation({
    mutationFn: () => apiFetch<{ turned_on: number }>("/api/v1/ac/all-on", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const roomLampsOff = useMutation({
    mutationFn: (roomId: number) =>
      apiFetch<{ turned_off: number }>(`/api/v1/rooms/${roomId}/lamps/all-off`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const roomLampsOn = useMutation({
    mutationFn: (roomId: number) =>
      apiFetch<{ turned_on: number }>(`/api/v1/rooms/${roomId}/lamps/all-on`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const roomAcOff = useMutation({
    mutationFn: (roomId: number) =>
      apiFetch<{ turned_off: number }>(`/api/v1/rooms/${roomId}/ac/all-off`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["rooms-overview"] }),
  });

  const roomAcOn = useMutation({
    mutationFn: (roomId: number) =>
      apiFetch<{ turned_on: number }>(`/api/v1/rooms/${roomId}/ac/all-on`, { method: "POST" }),
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
          <p className="muted">
            Visualize lâmpadas e ar-condicionado. Clique na sala para controle detalhado.
          </p>
        </div>
        {canBulk && (
          <div className="bulk-actions bulk-actions-stacked">
            <div className="bulk-actions-row">
              <span className="toolbar-label">Lâmpadas</span>
              <button type="button" className="btn-secondary" disabled={allLampsOn.isPending} onClick={() => allLampsOn.mutate()}>
                Ligar todas
              </button>
              <button type="button" className="btn-danger-outline" disabled={allLampsOff.isPending} onClick={() => allLampsOff.mutate()}>
                Desligar todas
              </button>
            </div>
            <div className="bulk-actions-row">
              <span className="toolbar-label">Ar</span>
              <button type="button" className="btn-secondary" disabled={allAcOn.isPending} onClick={() => allAcOn.mutate()}>
                Ligar todos
              </button>
              <button type="button" className="btn-danger-outline" disabled={allAcOff.isPending} onClick={() => allAcOff.mutate()}>
                Desligar todos
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="room-overview-grid">
        {data?.map((room) => (
          <div key={room.id} className="card room-overview-card">
            <Link to={`/salas/${room.id}`} className="room-overview-link">
              <RoomPreviewMini
                lamps={room.lamps}
                airConditioners={room.air_conditioners}
                roomName={room.name}
                roomCode={room.code}
              />
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
                    disabled={roomLampsOn.isPending}
                    onClick={() => roomLampsOn.mutate(room.id)}
                  >
                    Ligar lâmpadas
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    disabled={roomLampsOff.isPending}
                    onClick={() => roomLampsOff.mutate(room.id)}
                  >
                    Desligar lâmpadas
                  </button>
                  {room.air_conditioners.length > 0 && (
                    <>
                      <button
                        type="button"
                        className="btn-secondary"
                        disabled={roomAcOn.isPending}
                        onClick={() => roomAcOn.mutate(room.id)}
                      >
                        Ligar ar
                      </button>
                      <button
                        type="button"
                        className="btn-secondary"
                        disabled={roomAcOff.isPending}
                        onClick={() => roomAcOff.mutate(room.id)}
                      >
                        Desligar ar
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
