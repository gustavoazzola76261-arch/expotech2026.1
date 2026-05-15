import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { Lamp, LampSchedule, Me, Room, RoomOverview, ScheduleScope } from "../types";
import { WEEKDAYS } from "../types";

async function fetchSchedules(): Promise<LampSchedule[]> {
  return apiFetch<LampSchedule[]>("/api/v1/schedules");
}

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

async function fetchOverview(): Promise<RoomOverview[]> {
  return apiFetch<RoomOverview[]>("/api/v1/rooms/overview");
}

function toggleId(list: number[], id: number): number[] {
  return list.includes(id) ? list.filter((x) => x !== id) : [...list, id];
}

export function SchedulesPage() {
  const qc = useQueryClient();
  const { data: me } = useQuery({ queryKey: ["me"], queryFn: () => apiFetch<Me>("/api/v1/me") });
  const { data, isLoading, error } = useQuery({
    queryKey: ["schedules"],
    queryFn: fetchSchedules,
    enabled: me?.role === "admin" || me?.role === "mestre",
  });
  const { data: rooms } = useQuery({
    queryKey: ["rooms"],
    queryFn: fetchRooms,
    enabled: me?.role === "admin" || me?.role === "mestre",
  });
  const { data: overview } = useQuery({
    queryKey: ["rooms-overview"],
    queryFn: fetchOverview,
    enabled: me?.role === "admin" || me?.role === "mestre",
  });

  const allLamps = useMemo(() => {
    const lamps: Lamp[] = [];
    for (const room of overview ?? []) {
      for (const lamp of room.lamps) {
        lamps.push(lamp);
      }
    }
    return lamps.sort((a, b) => a.room_id - b.room_id || a.slot - b.slot);
  }, [overview]);

  const [name, setName] = useState("");
  const [scope, setScope] = useState<ScheduleScope>("all");
  const [action, setAction] = useState<"on" | "off">("on");
  const [hour, setHour] = useState(6);
  const [minute, setMinute] = useState(0);
  const [roomId, setRoomId] = useState(1);
  const [lampId, setLampId] = useState(1);
  const [selectedRoomIds, setSelectedRoomIds] = useState<number[]>([]);
  const [selectedLampIds, setSelectedLampIds] = useState<number[]>([]);
  const [selectedDays, setSelectedDays] = useState<number[]>([]);
  const [allDays, setAllDays] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);

  const saveSchedule = useMutation({
    mutationFn: () => {
      const json = {
        name,
        scope,
        action,
        hour,
        minute,
        room_id: scope === "room" ? roomId : null,
        lamp_id: scope === "lamp" ? lampId : null,
        room_ids: scope === "rooms_group" ? selectedRoomIds : null,
        lamp_ids: scope === "lamps_group" ? selectedLampIds : null,
        days_of_week: allDays ? null : selectedDays,
        is_enabled: true,
      };
      if (editingId) {
        return apiFetch<LampSchedule>(`/api/v1/schedules/${editingId}`, { method: "PATCH", json });
      }
      return apiFetch<LampSchedule>("/api/v1/schedules", { method: "POST", json });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["schedules"] });
      setName("");
      setEditingId(null);
      setSelectedRoomIds([]);
      setSelectedLampIds([]);
      setSelectedDays([]);
      setAllDays(true);
    },
  });

  const remove = useMutation({
    mutationFn: (id: number) => apiFetch<void>(`/api/v1/schedules/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["schedules"] }),
  });

  if (me?.role !== "admin" && me?.role !== "mestre") return <Navigate to="/" replace />;
  if (isLoading) return <p className="muted">Carregando programações…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!allDays && selectedDays.length === 0) {
      return;
    }
    saveSchedule.mutate();
  }

  function loadForEdit(s: LampSchedule) {
    setEditingId(s.id);
    setName(s.name);
    setScope(s.scope);
    setAction(s.action);
    setHour(s.hour);
    setMinute(s.minute);
    setRoomId(s.room_id ?? rooms?.[0]?.id ?? 1);
    setLampId(s.lamp_id ?? allLamps[0]?.id ?? 1);
    setSelectedRoomIds(s.room_ids ?? []);
    setSelectedLampIds(s.lamp_ids ?? []);
    const days = s.days_of_week ?? [];
    setAllDays(days.length === 0);
    setSelectedDays(days);
  }

  function cancelEdit() {
    setEditingId(null);
    setName("");
    setSelectedRoomIds([]);
    setSelectedLampIds([]);
    setSelectedDays([]);
    setAllDays(true);
  }

  function toggleDay(day: number) {
    setSelectedDays((prev) => (prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]));
  }

  function formatTime(h: number, m: number) {
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
  }

  function targetLabel(s: LampSchedule) {
    if (s.target_label) return s.target_label;
    if (s.scope === "all") return "Todas as lâmpadas";
    if (s.scope === "room") return s.room_name ? `Sala: ${s.room_name}` : `Sala ID ${s.room_id}`;
    if (s.scope === "rooms_group") return `Grupo de salas (${s.room_ids?.length ?? 0})`;
    if (s.scope === "lamp") return s.lamp_name ? `Lâmpada: ${s.lamp_name}` : `Lâmpada ID ${s.lamp_id}`;
    return `Grupo de lâmpadas (${s.lamp_ids?.length ?? 0})`;
  }

  return (
    <div>
      <h2>Programação</h2>
      <p className="muted">Agende ligar ou desligar por horário e dias da semana (fuso America/Sao_Paulo).</p>

      <div className="two-col">
        <div className="card">
          <h3>{editingId ? "Editar programação" : "Nova programação"}</h3>
          <form className="stack" onSubmit={onSubmit}>
            <label>
              Nome
              <input value={name} onChange={(e) => setName(e.target.value)} required placeholder="Ex: Acender manhã" />
            </label>
            <label>
              Escopo
              <select value={scope} onChange={(e) => setScope(e.target.value as ScheduleScope)}>
                <option value="all">Todas as lâmpadas</option>
                <option value="room">Sala específica</option>
                <option value="rooms_group">Grupo de salas</option>
                <option value="lamp">Lâmpada específica</option>
                <option value="lamps_group">Grupo de lâmpadas</option>
              </select>
            </label>
            {scope === "room" && (
              <label>
                Sala
                <select value={roomId} onChange={(e) => setRoomId(Number(e.target.value))}>
                  {rooms?.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name} (ID {r.id})
                    </option>
                  ))}
                </select>
              </label>
            )}
            {scope === "rooms_group" && (
              <fieldset className="checkbox-group">
                <legend>Salas do grupo</legend>
                {rooms?.map((r) => (
                  <label key={r.id} className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={selectedRoomIds.includes(r.id)}
                      onChange={() => setSelectedRoomIds((prev) => toggleId(prev, r.id))}
                    />
                    {r.name} (ID {r.id})
                  </label>
                ))}
              </fieldset>
            )}
            {scope === "lamp" && (
              <label>
                Lâmpada
                <select value={lampId} onChange={(e) => setLampId(Number(e.target.value))}>
                  {allLamps.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.name} — sala {l.room_id}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {scope === "lamps_group" && (
              <fieldset className="checkbox-group">
                <legend>Lâmpadas do grupo</legend>
                {allLamps.map((l) => (
                  <label key={l.id} className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={selectedLampIds.includes(l.id)}
                      onChange={() => setSelectedLampIds((prev) => toggleId(prev, l.id))}
                    />
                    {l.name} (sala {l.room_id})
                  </label>
                ))}
              </fieldset>
            )}
            <label>
              Ação
              <select value={action} onChange={(e) => setAction(e.target.value as "on" | "off")}>
                <option value="on">Ligar</option>
                <option value="off">Desligar</option>
              </select>
            </label>
            <fieldset className="checkbox-group">
              <legend>Dias da semana</legend>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={allDays}
                  onChange={(e) => {
                    setAllDays(e.target.checked);
                    if (e.target.checked) setSelectedDays([]);
                  }}
                />
                Todos os dias
              </label>
              {!allDays &&
                WEEKDAYS.map((d) => (
                  <label key={d.value} className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={selectedDays.includes(d.value)}
                      onChange={() => toggleDay(d.value)}
                    />
                    {d.label}
                  </label>
                ))}
            </fieldset>
            <div className="time-row">
              <label>
                Hora
                <input type="number" min={0} max={23} value={hour} onChange={(e) => setHour(Number(e.target.value))} />
              </label>
              <label>
                Minuto
                <input type="number" min={0} max={59} value={minute} onChange={(e) => setMinute(Number(e.target.value))} />
              </label>
            </div>
            {!allDays && selectedDays.length === 0 && (
              <p className="muted small">Selecione ao menos um dia ou marque &quot;Todos os dias&quot;.</p>
            )}
            {saveSchedule.error && <div className="error-banner">{(saveSchedule.error as Error).message}</div>}
            <div className="modal-actions">
              {editingId && (
                <button type="button" className="btn-secondary" onClick={cancelEdit}>
                  Cancelar edição
                </button>
              )}
              <button type="submit" disabled={saveSchedule.isPending || (!allDays && selectedDays.length === 0)}>
                {editingId ? "Salvar alterações" : "Criar programação"}
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <h3>Programações cadastradas</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Alvo</th>
                <th>Dias</th>
                <th>Horário</th>
                <th>Ação</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data?.length === 0 && (
                <tr>
                  <td colSpan={6} className="muted">
                    Nenhuma programação cadastrada.
                  </td>
                </tr>
              )}
              {data?.map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{targetLabel(s)}</td>
                  <td>{s.days_label ?? "Todos os dias"}</td>
                  <td>{formatTime(s.hour, s.minute)}</td>
                  <td>{s.action === "on" ? "Ligar" : "Desligar"}</td>
                  <td className="table-actions-cell">
                    <button type="button" className="btn-secondary" onClick={() => loadForEdit(s)}>
                      Editar
                    </button>
                    <button type="button" className="btn-secondary" onClick={() => remove.mutate(s.id)}>
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
