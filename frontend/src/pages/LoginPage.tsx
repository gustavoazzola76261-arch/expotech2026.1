import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiFetch, loginRequest, setToken } from "../api/client";
import type { Me } from "../types";

export function LoginPage() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await loginRequest(email, password);
      setToken(res.access_token);
      try {
        const me = await apiFetch<Me>("/api/v1/me");
        if (me.role === "professor" && me.room_ids.length > 0) {
          nav(`/salas/${me.room_ids[0]}`, { replace: true });
        } else {
          nav("/", { replace: true });
        }
      } catch (inner) {
        setToken(null);
        const msg = inner instanceof Error ? inner.message : "Erro desconhecido";
        setError(`Token válido, mas falhou ao carregar o perfil: ${msg}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login-card" onSubmit={onSubmit}>
        <h1>Campus IoT</h1>
        <p className="muted">OAuth2 (password) + JWT</p>
        <label>
          E-mail
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoComplete="username" />
        </label>
        <label>
          Senha
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete="current-password"
          />
        </label>
        {error && <div className="error-banner">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </div>
  );
}
