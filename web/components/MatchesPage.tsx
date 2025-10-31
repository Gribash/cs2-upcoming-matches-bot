"use client";
import { useEffect, useMemo, useState } from "react";
import { fetchMatches } from "../lib/api";
import type { Match } from "../lib/types";
import MatchCard from "./MatchCard";

export default function MatchesPage({ endpoint, title }: { endpoint: string; title: string }) {
  const [tier, setTier] = useState<"1" | "all">(() => (typeof window !== "undefined" ? (localStorage.getItem("tier") as "1" | "all") || "1" : "1"));
  const [data, setData] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem("tier", tier);
  }, [tier]);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    fetchMatches(endpoint, { tier, limit: 50 })
      .then((res) => mounted && setData(res))
      .catch((e) => mounted && setError(e?.message || "Error"))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [endpoint, tier]);

  const content = useMemo(() => {
    if (loading) return <div className="muted">Loading…</div>;
    if (error) return <div className="error">{error}</div>;
    if (!data.length) return <div className="muted">Нет данных</div>;
    return (
      <div className="grid">
        {data.map((m) => (
          <MatchCard key={m.id} match={m} />)
        )}
      </div>
    );
  }, [loading, error, data]);

  return (
    <section>
      <div className="row">
        <h1>{title}</h1>
        <div className="toggle">
          <button className={tier === "1" ? "active" : ""} onClick={() => setTier("1")}>
            Top Tier
          </button>
          <button className={tier === "all" ? "active" : ""} onClick={() => setTier("all")}>
            All
          </button>
        </div>
      </div>
      {content}
    </section>
  );
}


