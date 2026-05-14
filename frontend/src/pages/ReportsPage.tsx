import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiFetch } from "../api/client";
import type { ConsumptionMonthlyResponse, Me } from "../types";

const WINDOW_OPTIONS = [
  { value: 1 as const, label: "Este mês" },
  { value: 3 as const, label: "Últimos 3 meses" },
  { value: 6 as const, label: "Últimos 6 meses" },
  { value: 12 as const, label: "Últimos 12 meses" },
];

function monthLabel(ym: string): string {
  const [y, m] = ym.split("-").map(Number);
  if (!y || !m) return ym;
  return new Date(y, m - 1, 1).toLocaleDateString("pt-BR", { month: "short", year: "numeric" });
}

async function fetchMonthly(months: number): Promise<ConsumptionMonthlyResponse> {
  return apiFetch<ConsumptionMonthlyResponse>(`/api/v1/consumption/monthly?months=${months}`);
}

export function ReportsPage() {
  const [months, setMonths] = useState<1 | 3 | 6 | 12>(12);
  const { data: me, isLoading: loadingMe } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data, isLoading, error } = useQuery({
    queryKey: ["consumption-monthly", months],
    queryFn: () => fetchMonthly(months),
    enabled: me?.role === "admin",
  });

  const chartData = useMemo(
    () =>
      (data?.points ?? []).map((p) => ({
        ...p,
        label: monthLabel(p.year_month),
        kwhNum: Number(p.kwh),
      })),
    [data?.points],
  );

  if (loadingMe) return <p className="muted">Carregando…</p>;
  if (me?.role !== "admin") return <Navigate to="/" replace />;

  if (isLoading) return <p className="muted">Carregando consumo…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;

  return (
    <div>
      <h2>Consumo de energia</h2>
      <p className="muted">kWh registrados ao desligar lâmpadas (estimativa por período ligado). Somente administradores.</p>

      <div className="consumption-toolbar card">
        <span className="toolbar-label">Período</span>
        <div className="filter-chips">
          {WINDOW_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              className={months === opt.value ? "chip chip-active" : "chip"}
              onClick={() => setMonths(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
        <div className="period-total">
          <span className="muted">Total no período</span>
          <strong>{data?.total_kwh_in_period ?? "0"} kWh</strong>
        </div>
      </div>

      <div className="card chart-card">
        <h3 className="chart-title">Consumo mês a mês (kWh)</h3>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={chartData} margin={{ top: 16, right: 16, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 12 }} interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} tickFormatter={(v) => `${v}`} width={48} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                formatter={(value: number) => [`${Number(value).toFixed(4)} kWh`, "Consumo"]}
              />
              <Bar dataKey="kwhNum" fill="#38bdf8" radius={[4, 4, 0, 0]} name="kWh" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
