const TOKEN_KEY = "campus_iot_token";

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
  else sessionStorage.removeItem(TOKEN_KEY);
}

const apiBase = import.meta.env.VITE_API_URL ?? "";

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { json?: unknown } = {},
): Promise<T> {
  const { json, ...rest } = options;
  const headers = new Headers(rest.headers);
  if (json !== undefined) headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${apiBase}${path}`, {
    ...rest,
    headers,
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
      else if (Array.isArray(body?.detail))
        detail = body.detail.map((d: { msg?: string }) => d.msg).join(", ");
    } catch {
      if (res.status >= 500) detail = `Erro no servidor (${res.status}). Verifique o terminal do uvicorn.`;
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export async function loginRequest(email: string, password: string) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);
  const res = await fetch(`${apiBase}/api/v1/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) {
    let detail = "Falha no login";
    try {
      const err = await res.json();
      if (typeof err.detail === "string") detail = err.detail;
      else if (Array.isArray(err.detail)) detail = err.detail.map((d: { msg?: string }) => d.msg).join(", ");
    } catch {
      if (res.status >= 500) detail = `Erro no servidor (${res.status}). Verifique o terminal do uvicorn.`;
    }
    throw new Error(detail);
  }
  return (await res.json()) as { access_token: string; token_type: string };
}
