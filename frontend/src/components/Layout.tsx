import { NavLink, Outlet } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { apiFetch, setToken } from "../api/client";
import type { Me, Room } from "../types";

async function fetchMe(): Promise<Me> {
  return apiFetch<Me>("/api/v1/me");
}

async function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>("/api/v1/rooms");
}

export function Layout() {
  const { data: me } = useQuery({ queryKey: ["me"], queryFn: fetchMe });
  const { data: professorRooms } = useQuery({
    queryKey: ["rooms"],
    queryFn: fetchRooms,
    enabled: me?.role === "professor",
  });

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">Campus IoT</div>
        <nav>
          {me?.role === "professor" ? (
            <>
              {professorRooms && professorRooms.length > 0 ? (
                professorRooms.map((r) => (
                  <NavLink key={r.id} to={`/salas/${r.id}`}>
                    {r.name}
                  </NavLink>
                ))
              ) : (
                <span className="nav-muted">Nenhuma sala atribuída</span>
              )}
            </>
          ) : (
            <NavLink to="/" end>
              Salas
            </NavLink>
          )}
          {me?.role === "admin" && (
            <>
              <NavLink to="/relatorios">Consumo</NavLink>
              <NavLink to="/admin/usuarios">Usuários</NavLink>
            </>
          )}
        </nav>
        <div className="sidebar-footer">
          {me && (
            <div className="user-chip">
              <div className="user-name">{me.full_name}</div>
              <div className="user-role">{me.role}</div>
            </div>
          )}
          <button
            type="button"
            className="link-button"
            onClick={() => {
              setToken(null);
              window.location.href = "/login";
            }}
          >
            Sair
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
