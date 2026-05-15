import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { Me, Room } from "../types";

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

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
  const [editing, setEditing] = useState<Room | null>(null);
  const [editName, setEditName] = useState("");
  const [editCode, setEditCode] = useState("");
  const [editNewId, setEditNewId] = useState("");

  const createRoom = useMutation({
    mutationFn: () => {
      const body: { name: string; code: string; id?: number } = {
        name: name.trim(),
        code: code.trim().toUpperCase(),
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
    },
  });

  const updateRoom = useMutation({
    mutationFn: ({ id, body }: { id: number; body: { name: string; code: string; new_id?: number } }) =>
      apiFetch<Room>(`/api/v1/rooms/${id}`, { method: "PATCH", json: body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["rooms"] });
      qc.invalidateQueries({ queryKey: ["rooms-overview"] });
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

  function openEdit(room: Room) {
    setEditing(room);
    setEditName(room.name);
    setEditCode(room.code);
    setEditNewId(String(room.id));
  }

  function onEditSubmit(e: FormEvent) {
    e.preventDefault();
    if (!editing) return;
    const body: { name: string; code: string; new_id?: number } = {
      name: editName.trim(),
      code: editCode.trim().toUpperCase(),
    };
    const newId = parseInt(editNewId.trim(), 10);
    if (editNewId.trim() && newId !== editing.id) body.new_id = newId;
    updateRoom.mutate({ id: editing.id, body });
  }

  return (
    <div>
      <h2>Gerenciar salas</h2>
      <p className="muted">Adicione ou edite salas. Cada nova sala recebe automaticamente 3 lâmpadas.</p>

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
        <div className="modal-backdrop" role="presentation" onClick={() => !updateRoom.isPending && setEditing(null)}>
          <div className="modal-panel card" role="dialog" aria-modal onClick={(e) => e.stopPropagation()}>
            <h3>Editar sala</h3>
            <p className="muted small">ID {editing.id}</p>
            <form className="stack" onSubmit={onEditSubmit}>
              <label>
                Nome
                <input value={editName} onChange={(e) => setEditName(e.target.value)} required />
              </label>
              <label>
                Código
                <input value={editCode} onChange={(e) => setEditCode(e.target.value)} required />
              </label>
              <label>
                ID da sala
                <input value={editNewId} onChange={(e) => setEditNewId(e.target.value)} type="number" min={1} required />
              </label>
              <p className="muted small">
                Para alinhar IDs (ex.: sala “1” com ID 1 em vez de 6): informe o novo ID livre e salve.
              </p>
              {updateRoom.error && <div className="error-banner">{(updateRoom.error as Error).message}</div>}
              <div className="modal-actions">
                <button type="button" className="btn-secondary" disabled={updateRoom.isPending} onClick={() => setEditing(null)}>
                  Cancelar
                </button>
                <button type="submit" disabled={updateRoom.isPending}>
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
