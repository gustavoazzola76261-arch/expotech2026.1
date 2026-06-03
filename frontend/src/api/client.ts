const TOKEN_KEY = "campus_iot_token";

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
  else sessionStorage.removeItem(TOKEN_KEY);
}

const apiBase = import.meta.env.VITE_API_URL ?? "";

/** Extrai mensagem segura de erro (RFC 7807 Problem Details ou legado FastAPI). */
export function parseApiError(body: unknown, status: number): string {
  if (body && typeof body === "object") {
    const record = body as Record<string, unknown>;
    if (typeof record.detail === "string" && record.detail.trim()) {
      return record.detail;
    }
    if (typeof record.message === "string" && record.message.trim()) {
      return record.message;
    }
    if (Array.isArray(record.detail)) {
      return "Os dados enviados são inválidos.";
    }
  }
  if (status === 401) return "Não foi possível autenticar.";
  if (status === 403) return "Você não tem permissão para esta ação.";
  if (status === 404) return "Recurso não encontrado.";
  if (status === 429) return "Muitas requisições. Tente novamente em instantes.";
  if (status >= 500) return "Erro interno. Tente novamente mais tarde.";
  return "Não foi possível concluir a operação.";
}

export type ActionResult = {
  message: string;
  data: Record<string, number>;
};

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
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    throw new Error(parseApiError(body, res.status));
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
    let errBody: unknown;
    try {
      errBody = await res.json();
    } catch {
      errBody = null;
    }
    throw new Error(parseApiError(errBody, res.status));
  }
  return (await res.json()) as { access_token: string; token_type: string };
}
