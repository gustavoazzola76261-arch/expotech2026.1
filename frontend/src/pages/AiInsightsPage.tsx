import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { IALastReportResponse, IAInsightsResponse, Me, Room } from "../types";

const WINDOW_OPTIONS = [
  { value: 1 as const, label: "Este mês" },
  { value: 3 as const, label: "3 meses" },
  { value: 6 as const, label: "6 meses" },
  { value: 12 as const, label: "12 meses" },
];

const DEFAULT_CONTEXT =
  "Faculdade aberta de segunda a sexta, das 9h às 22h. Aulas nos horários: 10h–13h, 14h–17h e 19h–22h.";

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

function ReportSections({ data }: { data: IALastReportResponse | IAInsightsResponse }) {
  return (
    <>
      <section className="card ia-section">
        <h3>Análise de consumo</h3>
        <p className="ia-text">{data.analysis}</p>
      </section>
      <section className="card ia-section">
        <h3>Relatório</h3>
        <p className="ia-text">{data.report}</p>
      </section>
      <section className="card ia-section">
        <h3>Sugestões para reduzir gasto</h3>
        {(data.savings_suggestions?.length ?? 0) === 0 ? (
          <p className="muted">Nenhuma sugestão retornada.</p>
        ) : (
          <ul className="ia-list">
            {data.savings_suggestions!.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        )}
      </section>
      <section className="card ia-section ia-section-alert">
        <h3>Detecção de desperdício</h3>
        {(data.waste_detection?.length ?? 0) === 0 ? (
          <p className="muted">Nenhum alerta retornado.</p>
        ) : (
          <ul className="ia-list">
            {data.waste_detection!.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}

export function AiInsightsPage() {
  const qc = useQueryClient();
  const [months, setMonths] = useState<1 | 3 | 6 | 12>(12);
  const [roomId, setRoomId] = useState<number | "">("");
  const [operationContext, setOperationContext] = useState("");

  const { data: me, isLoading: loadingMe } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data: rooms } = useQuery({
    queryKey: ["rooms"],
    queryFn: fetchRooms,
    enabled: me?.role === "admin",
  });
  const { data: savedContext } = useQuery({
    queryKey: ["ia-operation-context"],
    queryFn: () => apiFetch<{ operation_context: string | null }>("/api/v1/ia/operation-context"),
    enabled: me?.role === "admin",
  });
  const { data: lastReport, isLoading: loadingLast } = useQuery({
    queryKey: ["ia-last-report"],
    queryFn: () => apiFetch<IALastReportResponse>("/api/v1/ia/last-report"),
    enabled: me?.role === "admin",
  });

  useEffect(() => {
    if (savedContext?.operation_context != null) {
      setOperationContext(savedContext.operation_context);
    }
  }, [savedContext?.operation_context]);

  const saveContext = useMutation({
    mutationFn: () =>
      apiFetch<{ operation_context: string | null }>("/api/v1/ia/operation-context", {
        method: "PUT",
        json: { operation_context: operationContext },
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ia-operation-context"] }),
  });

  const insights = useMutation({
    mutationFn: () => {
      const params = new URLSearchParams({ months: String(months) });
      if (roomId !== "") params.set("room_id", String(roomId));
      return apiFetch<IAInsightsResponse>(`/api/v1/ia/insights?${params}`, { method: "POST" });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ia-last-report"] });
    },
  });

  if (loadingMe) return <p className="muted">Carregando…</p>;
  if (me?.role !== "admin") return <Navigate to="/" replace />;

  const displayReport: IALastReportResponse | IAInsightsResponse | null =
    insights.data ?? (lastReport?.has_report ? lastReport : null);

  const generatedLabel = displayReport?.generated_at
    ? new Date(displayReport.generated_at).toLocaleString("pt-BR")
    : null;

  return (
    <div className="ia-page">
      <h2>Inteligência artificial</h2>
      <p className="muted">
        Análise objetiva do Campus IoT: salas com maior consumo, horários críticos e desperdício fora do funcionamento
        do campus.
      </p>

      <div className="card ia-context-card">
        <h3>Contexto operacional do campus</h3>
        <p className="muted small">
          Descreva dias e horários de funcionamento e de aulas. A IA usa isso para detectar desperdício (ex.: lâmpadas
          ligadas à noite ou aos sábados).
        </p>
        <textarea
          className="ia-context-textarea"
          rows={5}
          value={operationContext}
          onChange={(e) => setOperationContext(e.target.value)}
          placeholder={DEFAULT_CONTEXT}
        />
        <div className="modal-actions">
          <button type="button" className="btn-secondary" onClick={() => setOperationContext(DEFAULT_CONTEXT)}>
            Usar exemplo
          </button>
          <button type="button" disabled={saveContext.isPending} onClick={() => saveContext.mutate()}>
            {saveContext.isPending ? "Salvando…" : "Salvar contexto"}
          </button>
        </div>
        {saveContext.isSuccess && <p className="muted small">Contexto salvo.</p>}
      </div>

      <div className="card ia-toolbar">
        <div className="ia-filters">
          <label>
            Período
            <select value={months} onChange={(e) => setMonths(Number(e.target.value) as 1 | 3 | 6 | 12)}>
              {WINDOW_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Sala (opcional)
            <select value={roomId} onChange={(e) => setRoomId(e.target.value === "" ? "" : Number(e.target.value))}>
              <option value="">Todas as salas</option>
              {rooms?.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </label>
        </div>
        <button type="button" disabled={insights.isPending} onClick={() => insights.mutate()}>
          {insights.isPending ? "Gerando análise… (1–2 min)" : "Gerar nova análise"}
        </button>
      </div>

      {insights.error && <div className="error-banner">{(insights.error as Error).message}</div>}

      {loadingLast && !displayReport && <p className="muted">Carregando último relatório…</p>}

      {displayReport && (
        <div className="ia-results">
          <div className="ia-last-meta card">
            <h3>Último relatório salvo</h3>
            {generatedLabel && (
              <p>
                <strong>Data e hora:</strong> {generatedLabel}
              </p>
            )}
            {"model" in displayReport && displayReport.model && (
              <p className="muted small">Modelo: {displayReport.model}</p>
            )}
            {insights.data && <p className="muted small">Relatório recém-gerado (já persistido no servidor).</p>}
          </div>
          <ReportSections data={displayReport} />
        </div>
      )}

      {!loadingLast && !displayReport && (
        <p className="muted">Nenhum relatório salvo ainda. Salve o contexto e clique em &quot;Gerar nova análise&quot;.</p>
      )}
    </div>
  );
}
