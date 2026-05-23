import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import { MAX_AC_UNITS_PER_ROOM } from "../components/acLayout";
import { MAX_LAMPS_PER_ROOM } from "../components/lampLayout";
import type { AirConditioner, Lamp, Me, Room } from "../types";

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

async function fetchRoomLamps(roomId: number): Promise<Lamp[]> {
  return apiFetch<Lamp[]>(`/api/v1/rooms/${roomId}/lamps`);
}

async function fetchRoomAc(roomId: number): Promise<AirConditioner[]> {
  return apiFetch<AirConditioner[]>(`/api/v1/rooms/${roomId}/ac`);
}

type PowerDraft = { power_watts: number };

export function RoomsManagePage() {
  const qc = useQueryClient();
  const { data: me, isLoading: loadingMe } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<Me>("/api/v1/me"),
  });
  const { data, isLoading, error } = useQuery({
    queryKey: ["rooms"],
    queryFn: fetchRooms,
    enabled: me?.role === "admin" || me?.role === "mestre",
  });

  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [newRoomId, setNewRoomId] = useState("");
  const [createLampCount, setCreateLampCount] = useState(3);
  const [createDefaultPower, setCreateDefaultPower] = useState(20);
  const [createAcCount, setCreateAcCount] = useState(1);
  const [createDefaultAcPower, setCreateDefaultAcPower] = useState(1500);

  const [editing, setEditing] = useState<Room | null>(null);
  const [editName, setEditName] = useState("");
  const [editCode, setEditCode] = useState("");
  const [editLamps, setEditLamps] = useState<PowerDraft[]>([]);
  const [editAc, setEditAc] = useState<PowerDraft[]>([]);
  const [loadingEditDevices, setLoadingEditDevices] = useState(false);

  const createRoom = useMutation({
    mutationFn: () => {
      const body: {
        name: string;
        code: string;
        id?: number;
        lamp_count: number;
        default_power_watts: number;
        ac_count: number;
        default_ac_power_watts: number;
      } = {
        name: name.trim(),
        code: code.trim().toUpperCase(),
        lamp_count: createLampCount,
        default_power_watts: createDefaultPower,
        ac_count: createAcCount,
        default_ac_power_watts: createDefaultAcPower,
      };
      const idNum = parseInt(newRoomId.trim(), 10);
      if (newRoomId.trim()) body.id = idNum;
      return apiFetch<Room>("/api/v1/rooms", { method: "POST", json: body });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["rooms"] });
      qc.invalidateQueries({ queryKey: ["rooms-overview"] });
      setName("");
      setCode("");
      setNewRoomId("");
      setCreateLampCount(3);
      setCreateDefaultPower(20);
      setCreateAcCount(1);
      setCreateDefaultAcPower(1500);
    },
  });

  const updateRoom = useMutation({
    mutationFn: ({
      id,
      body,
    }: {
      id: number;
      body: {
        name: string;
        code: string;
        lamps: { power_watts: number }[];
        air_conditioners: { power_watts: number }[];
      };
    }) => apiFetch<Room>(`/api/v1/rooms/${id}`, { method: "PATCH", json: body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["rooms"] });
      qc.invalidateQueries({ queryKey: ["rooms-overview"] });
      qc.invalidateQueries({ queryKey: ["lamps"] });
      qc.invalidateQueries({ queryKey: ["ac"] });
      setEditing(null);
    },
  });

  const deleteRoom = useMutation({
    mutationFn: (id: number) => apiFetch<void>(`/api/v1/rooms/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["rooms"] });
      qc.invalidateQueries({ queryKey: ["rooms-overview"] });
      qc.invalidateQueries({ queryKey: ["lamps"] });
      setEditing(null);
    },
  });

  if (loadingMe) return <p className="muted">Carregando…</p>;
  if (me?.role !== "admin" && me?.role !== "mestre") return <Navigate to="/" replace />;
  if (isLoading) return <p className="muted">Carregando salas…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;

  function onCreate(e: FormEvent) {
    e.preventDefault();
    createRoom.mutate();
  }

  async function openEdit(room: Room) {
    setEditing(room);
    setEditName(room.name);
    setEditCode(room.code);
    setLoadingEditDevices(true);
    try {
      const [lamps, acUnits] = await Promise.all([fetchRoomLamps(room.id), fetchRoomAc(room.id)]);
      setEditLamps(
        lamps.length > 0
          ? lamps.sort((a, b) => a.slot - b.slot).map((l) => ({ power_watts: l.power_watts }))
          : [{ power_watts: 20 }],
      );
      setEditAc(acUnits.sort((a, b) => a.slot - b.slot).map((u) => ({ power_watts: u.power_watts })));
    } catch (err) {
      setEditLamps([{ power_watts: 20 }]);
      setEditAc([]);
      console.error(err);
    } finally {
      setLoadingEditDevices(false);
    }
  }

  function setLampCount(count: number) {
    const n = Math.min(MAX_LAMPS_PER_ROOM, Math.max(1, count));
    setEditLamps((prev) => {
      if (prev.length === n) return prev;
      if (prev.length < n) {
        const last = prev[prev.length - 1]?.power_watts ?? 20;
        return [...prev, ...Array.from({ length: n - prev.length }, () => ({ power_watts: last }))];
      }
      return prev.slice(0, n);
    });
  }

  function setAcCount(count: number) {
    const n = Math.min(MAX_AC_UNITS_PER_ROOM, Math.max(0, count));
    setEditAc((prev) => {
      if (prev.length === n) return prev;
      if (prev.length < n) {
        const last = prev[prev.length - 1]?.power_watts ?? 1500;
        return [...prev, ...Array.from({ length: n - prev.length }, () => ({ power_watts: last }))];
      }
      return prev.slice(0, n);
    });
  }

  function updateLampPower(index: number, power: number) {
    setEditLamps((prev) => prev.map((l, i) => (i === index ? { power_watts: power } : l)));
  }

  function updateAcPower(index: number, power: number) {
    setEditAc((prev) => prev.map((u, i) => (i === index ? { power_watts: power } : u)));
  }

  function onEditSubmit(e: FormEvent) {
    e.preventDefault();
    if (!editing) return;
    updateRoom.mutate({
      id: editing.id,
      body: {
        name: editName.trim(),
        code: editCode.trim().toUpperCase(),
        lamps: editLamps.map((l) => ({ power_watts: l.power_watts })),
        air_conditioners: editAc.map((u) => ({ power_watts: u.power_watts })),
      },
    });
  }

  function onDeleteRoom() {
    if (!editing) return;
    const ok = window.confirm(
      `Excluir a sala "${editing.name}" (${editing.code})? Todas as lâmpadas, aparelhos de ar e histórico vinculado serão removidos.`,
    );
    if (ok) deleteRoom.mutate(editing.id);
  }

  return (
    <div>
      <h2>Gerenciar salas</h2>
      <p className="muted">
        Configure lâmpadas e ar-condicionado (quantidade a partir de 0 para o ar, potência em watts). Os ícones nas salas acompanham essa configuração.
      </p>

      <div className="two-col">
        <div className="card">
          <h3>Nova sala</h3>
          <form className="stack" onSubmit={onCreate}>
            <label>
              Nome
              <input value={name} onChange={(e) => setName(e.target.value)} required placeholder="Ex: Sala 6" />
            </label>
            <label>
              Código
              <input value={code} onChange={(e) => setCode(e.target.value)} required placeholder="Ex: S6" />
            </label>
            <label>
              ID desejado (opcional)
              <input
                value={newRoomId}
                onChange={(e) => setNewRoomId(e.target.value)}
                placeholder="Ex: 1 — vazio = automático"
                type="number"
                min={1}
              />
            </label>
            <label>
              Quantidade de lâmpadas
              <input
                type="number"
                min={1}
                max={MAX_LAMPS_PER_ROOM}
                value={createLampCount}
                onChange={(e) => setCreateLampCount(Number(e.target.value))}
              />
            </label>
            <label>
              Potência padrão das lâmpadas (W)
              <input
                type="number"
                min={1}
                max={5000}
                value={createDefaultPower}
                onChange={(e) => setCreateDefaultPower(Number(e.target.value))}
              />
            </label>
            <label>
              Quantidade de ar-condicionado
              <input
                type="number"
                min={0}
                max={MAX_AC_UNITS_PER_ROOM}
                value={createAcCount}
                onChange={(e) => setCreateAcCount(Number(e.target.value))}
              />
            </label>
            <label>
              Potência padrão do ar (W)
              <input
                type="number"
                min={1}
                max={20000}
                value={createDefaultAcPower}
                onChange={(e) => setCreateDefaultAcPower(Number(e.target.value))}
                disabled={createAcCount === 0}
              />
            </label>
            {createRoom.error && <div className="error-banner">{(createRoom.error as Error).message}</div>}
            <button type="submit" disabled={createRoom.isPending}>
              Criar sala
            </button>
          </form>
        </div>

        <div className="card">
          <h3>Salas cadastradas</h3>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Código</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data?.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.name}</td>
                  <td>{r.code}</td>
                  <td>
                    <button type="button" className="btn-secondary" onClick={() => openEdit(r)}>
                      Editar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {editing && (
        <div className="modal-backdrop" role="presentation" onClick={() => !updateRoom.isPending && !deleteRoom.isPending && setEditing(null)}>
          <div className="modal-panel card modal-panel-wide" role="dialog" aria-modal onClick={(e) => e.stopPropagation()}>
            <h3>Editar sala</h3>
            <p className="muted small">ID da sala: {editing.id} (não editável)</p>

            {loadingEditDevices ? (
              <p className="muted">Carregando equipamentos…</p>
            ) : (
              <form className="stack" onSubmit={onEditSubmit}>
                <label>
                  Nome
                  <input value={editName} onChange={(e) => setEditName(e.target.value)} required />
                </label>
                <label>
                  Código
                  <input value={editCode} onChange={(e) => setEditCode(e.target.value)} required />
                </label>

                <div className="lamp-edit-block">
                  <label>
                    Quantidade de lâmpadas
                    <input
                      type="number"
                      min={1}
                      max={MAX_LAMPS_PER_ROOM}
                      value={editLamps.length}
                      onChange={(e) => setLampCount(Number(e.target.value))}
                    />
                  </label>
                  <p className="muted small">Potência de cada lâmpada (watts):</p>
                  <div className="lamp-power-grid">
                    {editLamps.map((lamp, index) => (
                      <label key={index} className="lamp-power-row">
                        <span>Lâmpada {index + 1}</span>
                        <input
                          type="number"
                          min={1}
                          max={5000}
                          value={lamp.power_watts}
                          onChange={(e) => updateLampPower(index, Number(e.target.value))}
                        />
                        <span className="muted small">W</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="lamp-edit-block">
                  <label>
                    Quantidade de ar-condicionado
                    <input
                      type="number"
                      min={0}
                      max={MAX_AC_UNITS_PER_ROOM}
                      value={editAc.length}
                      onChange={(e) => setAcCount(Number(e.target.value))}
                    />
                  </label>
                  {editAc.length > 0 && (
                    <>
                      <p className="muted small">Potência de cada aparelho (watts):</p>
                      <div className="lamp-power-grid">
                        {editAc.map((unit, index) => (
                          <label key={index} className="lamp-power-row">
                            <span>Ar {index + 1}</span>
                            <input
                              type="number"
                              min={1}
                              max={20000}
                              value={unit.power_watts}
                              onChange={(e) => updateAcPower(index, Number(e.target.value))}
                            />
                            <span className="muted small">W</span>
                          </label>
                        ))}
                      </div>
                    </>
                  )}
                </div>

                {updateRoom.error && <div className="error-banner">{(updateRoom.error as Error).message}</div>}
                {deleteRoom.error && <div className="error-banner">{(deleteRoom.error as Error).message}</div>}

                <div className="modal-actions modal-actions-split">
                  <button
                    type="button"
                    className="btn-danger-outline"
                    disabled={updateRoom.isPending || deleteRoom.isPending}
                    onClick={onDeleteRoom}
                  >
                    {deleteRoom.isPending ? "Excluindo…" : "Excluir sala"}
                  </button>
                  <div className="modal-actions">
                    <button
                      type="button"
                      className="btn-secondary"
                      disabled={updateRoom.isPending || deleteRoom.isPending}
                      onClick={() => setEditing(null)}
                    >
                      Cancelar
                    </button>
                    <button type="submit" disabled={updateRoom.isPending || deleteRoom.isPending}>
                      Salvar
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
