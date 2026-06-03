import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";

import { apiFetch } from "../api/client";
import type { AdminUser, UserRole } from "../types";

async function fetchUsers(): Promise<AdminUser[]> {
  return apiFetch<AdminUser[]>("/api/v1/admin/users");
}

type PatchBody = {
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  room_ids?: number[];
  password?: string;
};

export function AdminUsersPage() {
  const qc = useQueryClient();
  const { data: me, isLoading: loadingMe } = useQuery({
    queryKey: ["me"],
    queryFn: () => apiFetch<AdminUser>("/api/v1/me"),
  });
  const { data, isLoading, error } = useQuery({
    queryKey: ["admin-users"],
    queryFn: fetchUsers,
    enabled: me?.role === "admin",
  });

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("professor");
  const [roomIds, setRoomIds] = useState("1");

  const [editing, setEditing] = useState<AdminUser | null>(null);
  const [editEmail, setEditEmail] = useState("");
  const [editFullName, setEditFullName] = useState("");
  const [editRole, setEditRole] = useState<UserRole>("professor");
  const [editRoomIds, setEditRoomIds] = useState("");
  const [editActive, setEditActive] = useState(true);
  const [editPassword, setEditPassword] = useState("");
  const [editError, setEditError] = useState<string | null>(null);

  const create = useMutation({
    mutationFn: () =>
      apiFetch<AdminUser>("/api/v1/admin/users", {
        method: "POST",
        json: {
          email,
          full_name: fullName,
          password,
          role,
          room_ids: role === "professor" ? roomIds.split(",").map((s) => Number(s.trim())) : [],
        },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      setEmail("");
      setFullName("");
      setPassword("");
    },
  });

  const patchUser = useMutation({
    mutationFn: ({ id, body }: { id: number; body: PatchBody }) =>
      apiFetch<AdminUser>(`/api/v1/admin/users/${id}`, { method: "PATCH", json: body }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      setEditing(null);
      setEditPassword("");
      setEditError(null);
    },
  });

  function openEdit(u: AdminUser) {
    setEditing(u);
    setEditError(null);
    setEditEmail(u.email);
    setEditFullName(u.full_name);
    setEditRole(u.role);
    setEditRoomIds(u.room_ids?.length ? u.room_ids.join(", ") : "");
    setEditActive(u.is_active);
    setEditPassword("");
  }

  function onEditSubmit(e: FormEvent) {
    e.preventDefault();
    setEditError(null);
    if (!editing) return;
    const body: PatchBody = {
      email: editEmail.trim(),
      full_name: editFullName.trim(),
      role: editRole,
      is_active: editActive,
    };
    if (editRole === "professor") {
      const ids = editRoomIds
        .split(",")
        .map((s) => Number(s.trim()))
        .filter((n) => !Number.isNaN(n));
      if (ids.length === 0) {
        setEditError("Professor deve ter ao menos uma sala (IDs separados por vírgula).");
        return;
      }
      body.room_ids = ids;
    }
    const pw = editPassword.trim();
    if (pw) {
      if (pw.length < 8) {
        setEditError("Senha deve ter no mínimo 8 caracteres.");
        return;
      }
      body.password = pw;
    }
    patchUser.mutate({ id: editing.id, body });
  }

  if (loadingMe) return <p className="muted">Carregando…</p>;
  if (me && me.role !== "admin") return <Navigate to="/" replace />;

  function onCreate(e: FormEvent) {
    e.preventDefault();
    create.mutate();
  }

  if (isLoading) return <p className="muted">Carregando usuários…</p>;
  if (error) return <p className="error-banner">{(error as Error).message}</p>;

  return (
    <div>
      <h2>Usuários</h2>
      <div className="two-col">
        <div className="card">
          <h3>Novo usuário</h3>
          <form className="stack" onSubmit={onCreate}>
            <label>
              E-mail
              <input value={email} onChange={(e) => setEmail(e.target.value)} required type="email" />
            </label>
            <label>
              Nome
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            </label>
            <label>
              Senha (mín. 8)
              <input value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} type="password" />
            </label>
            <label>
              Perfil
              <select value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
                <option value="professor">Professor</option>
                <option value="mestre">Mestre</option>
                <option value="admin">Admin</option>
              </select>
            </label>
            {role === "professor" && (
              <label>
                IDs das salas (vírgula)
                <input value={roomIds} onChange={(e) => setRoomIds(e.target.value)} placeholder="ex: 1,2" />
              </label>
            )}
            {create.error && <div className="error-banner">{(create.error as Error).message}</div>}
            <button type="submit" disabled={create.isPending}>
              Criar
            </button>
          </form>
        </div>
        <div className="card">
          <h3>Lista</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Perfil</th>
                <th>Salas (prof.)</th>
                <th>Ativo</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data?.map((u) => (
                <tr key={u.id}>
                  <td>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td>{u.role}</td>
                  <td>{u.room_ids?.join(", ") || "—"}</td>
                  <td>{u.is_active ? "Sim" : "Não"}</td>
                  <td>
                    <button type="button" className="btn-secondary" onClick={() => openEdit(u)}>
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
        <div className="modal-backdrop" role="presentation" onClick={() => !patchUser.isPending && setEditing(null)}>
          <div className="modal-panel card" role="dialog" aria-modal onClick={(e) => e.stopPropagation()}>
            <h3>Editar usuário</h3>
            <p className="muted small">ID {editing.id}</p>
            <form className="stack" onSubmit={onEditSubmit}>
              <label>
                E-mail
                <input value={editEmail} onChange={(e) => setEditEmail(e.target.value)} required type="email" />
              </label>
              <label>
                Nome
                <input value={editFullName} onChange={(e) => setEditFullName(e.target.value)} required />
              </label>
              <label>
                Nova senha (opcional)
                <input
                  value={editPassword}
                  onChange={(e) => setEditPassword(e.target.value)}
                  type="password"
                  minLength={8}
                  placeholder="Deixe em branco para manter"
                  autoComplete="new-password"
                />
              </label>
              <label>
                Perfil
                <select value={editRole} onChange={(e) => setEditRole(e.target.value as UserRole)}>
                  <option value="professor">Professor</option>
                  <option value="mestre">Mestre</option>
                  <option value="admin">Admin</option>
                </select>
              </label>
              {editRole === "professor" && (
                <label>
                  IDs das salas (vírgula)
                  <input value={editRoomIds} onChange={(e) => setEditRoomIds(e.target.value)} placeholder="ex: 1,2" />
                </label>
              )}
              <label className="checkbox-row">
                <input type="checkbox" checked={editActive} onChange={(e) => setEditActive(e.target.checked)} />
                Conta ativa
              </label>
              {patchUser.error && <div className="error-banner">{(patchUser.error as Error).message}</div>}
              {editError && <div className="error-banner">{editError}</div>}
              <div className="modal-actions">
                <button type="button" className="btn-secondary" disabled={patchUser.isPending} onClick={() => setEditing(null)}>
                  Cancelar
                </button>
                <button type="submit" disabled={patchUser.isPending}>
                  Salvar alterações
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
