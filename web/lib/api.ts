import type { Match } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function fetchMatches(path: string, params: { tier: "1" | "all"; limit: number }): Promise<Match[]> {
  const url = new URL(path, API_BASE);
  url.searchParams.set("tier", params.tier);
  url.searchParams.set("limit", String(params.limit));
  const res = await fetch(url.toString(), { next: { revalidate: 30 } });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}


