import type { Match } from "../lib/types";

export default function MatchCard({ match }: { match: Match }) {
  const tournament = match.tournament?.name ?? "";
  const begin = match.begin_at || match.scheduled_at || "";
  const name = match.name || "Match";

  return (
    <article className="card">
      <div className="meta">
        <div className="tournament">{tournament}</div>
        <div className="time">{begin}</div>
      </div>
      <div className="title">{name}</div>
      <div className="actions">
        <a className="watch" href="#" onClick={(e) => e.preventDefault()}>Watch</a>
      </div>
    </article>
  );
}


