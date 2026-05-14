import { useQuery } from "@tanstack/react-query";
import { Link, Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { Me, Room } from "../types";

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

export function DashboardPage() {
  const { data: me, isLoading: loadingMe } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data, isLoading, error } = useQuery({
    queryKey: ["rooms"],
    queryFn: fetchRooms,
    enabled: !!me && me.role !== "professor",
  });

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
      <h2>Salas</h2>
      <p className="muted">Selecione uma sala para controlar as lâmpadas.</p>
      <div className="grid">
        {data?.map((r) => (
          <Link key={r.id} className="card room-card" to={`/salas/${r.id}`}>
            <div className="room-title">{r.name}</div>
            <div className="room-code">{r.code}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
