"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GIVECAMPUS_DONATE_URL } from "@/lib/donate";

type Team = {
  headline: string;
  body: string;
  donate_url: string;
  photos: { id: number; title: string; image_url: string; caption: string }[];
  players: { id: number; full_name: string; jersey_number?: string; position?: string }[];
};

export default function HomePage() {
  const [team, setTeam] = useState<Team | null>(null);
  const [error, setError] = useState("");
  const donateUrl = team?.donate_url || GIVECAMPUS_DONATE_URL;

  useEffect(() => {
    api<Team>("/public/team")
      .then(setTeam)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <main>
      <section className="hero">
        <p className="badge">University of Oregon · Club Rugby</p>
        <h1>Help keep the Ducks on the pitch.</h1>
        <p>
          Travel, kit, referees, and training add up fast for a student-run men&apos;s rugby program.
          Chip in through the university&apos;s GiveCampus form so your gift is processed for tax purposes.
        </p>
        <div style={{ display: "flex", gap: "0.8rem", marginTop: "1.5rem", flexWrap: "wrap" }}>
          <a className="btn" href={donateUrl}>
            Donate now
          </a>
          <Link className="btn secondary" href="/signup">
            I&apos;m a player
          </Link>
        </div>
      </section>

      {error && (
        <section className="section">
          <p className="error">{error}</p>
        </section>
      )}

      <section className="section" id="progress">
        <div className="card">
          <h2>Give through the University of Oregon</h2>
          <p className="muted">
            We no longer take payments on this site. Your donation opens on GiveCampus, the official
            UO channel, so receipts and tax handling stay with the university.
          </p>
          <a className="btn" href={donateUrl}>
            Continue to GiveCampus
          </a>
        </div>
      </section>

      <section className="section" id="team">
        <h2>{team?.headline || "The club"}</h2>
        <p style={{ maxWidth: "46rem", whiteSpace: "pre-wrap" }}>{team?.body}</p>
        <div className="photo-grid" style={{ marginTop: "1.5rem" }}>
          {team?.photos.map((p) => (
            <figure key={p.id}>
              <img src={p.image_url} alt={p.title} />
              <figcaption>
                <strong>{p.title}</strong>
                <div>{p.caption}</div>
              </figcaption>
            </figure>
          ))}
        </div>
        {team?.players?.length ? (
          <div className="card" style={{ marginTop: "1.5rem" }}>
            <h3>Roster</h3>
            <div className="grid-2">
              {team.players.map((p) => (
                <div key={p.id}>
                  <strong>{p.full_name}</strong>
                  <div className="muted">
                    {p.jersey_number ? `#${p.jersey_number}` : "Player"}
                    {p.position ? ` · ${p.position}` : ""}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
