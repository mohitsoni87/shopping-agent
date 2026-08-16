import type { ChatResponse, SearchPageResponse } from "./types";

const AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL ?? "http://localhost:8002";

export interface TenantContext {
  tenantId: string;
  env: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Request failed (${res.status}): ${body}`);
  }
  return res.json() as Promise<T>;
}

export function sendChatQuery(query: string, tenant: TenantContext): Promise<ChatResponse> {
  return fetch(`${AGENT_API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-tenant-id": tenant.tenantId,
      "x-env": tenant.env,
    },
    body: JSON.stringify({ query }),
  }).then((res) => handleResponse<ChatResponse>(res));
}

export function fetchSearchPage(
  searchId: string,
  offset: number,
  limit: number,
): Promise<SearchPageResponse> {
  const url = new URL(`${AGENT_API_URL}/search/${searchId}`);
  url.searchParams.set("offset", String(offset));
  url.searchParams.set("limit", String(limit));
  return fetch(url).then((res) => handleResponse<SearchPageResponse>(res));
}
