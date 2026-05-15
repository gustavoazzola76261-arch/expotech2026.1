import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { ActuationHistoryItem, Me } from "../types";

async function fetchHistory(): Promise<ActuationHistoryItem[]> {
  return apiFetch<ActuationHistoryItem[]>("/api/v1/admin/actuations?limit=200");
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("pt-BR");
}

function actionLabel(action: string) {
  return action === "on" ? "Ligou" : "Desligou";
}

export function ActuationHistoryPage() {
  const { data: me, isLoading: loadingMe } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data, isLoading, error } = useQuery({
    queryKey: ["actuation-history"],
    queryFn: fetchHistory,
    enabled: me?.role === "admin",
  });

  if (loadingMe) return <p className="muted">Carregando…</p>;
  if (me?.role !== "admin") return <Navigate to="/" replace />;
  if (isLoading) return <p className="muted">Carregando histórico…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;

  return (
    <div>
      <h2>Histórico de acionamentos</h2>
      <p className="muted">Quem acionou, em qual sala e qual lâmpada (últimos 200 registros).</p>
      <div className="card table-scroll">
        <table className="table">
          <thead>
            <tr>
              <th>Data/hora</th>
              <th>Usuário</th>
              <th>Sala</th>
              <th>Lâmpada</th>
              <th>Ação</th>
              <th>kWh (off)</th>
            </tr>
          </thead>
          <tbody>
            {data?.length === 0 && (
              <tr>
                <td colSpan={6} className="muted">
                  Nenhum acionamento registrado.
                </td>
              </tr>
            )}
            {data?.map((row) => (
              <tr key={row.id}>
                <td>{formatDate(row.created_at)}</td>
                <td>
                  {row.user_name ?? "—"}
                  {row.user_email ? <div className="muted small">{row.user_email}</div> : null}
                </td>
                <td>
                  {row.room_name}
                  <div className="muted small">{row.room_code}</div>
                </td>
                <td>
                  {row.lamp_name}
                  <div className="muted small">slot {row.lamp_slot}</div>
                </td>
                <td>
                  <span className={`action-badge action-${row.action}`}>{actionLabel(row.action)}</span>
                </td>
                <td>{row.energy_kwh != null ? row.energy_kwh : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
