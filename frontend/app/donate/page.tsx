"use client";

import { useEffect } from "react";
import { GIVECAMPUS_DONATE_URL } from "@/lib/donate";

export default function DonatePage() {
  useEffect(() => {
    window.location.replace(GIVECAMPUS_DONATE_URL);
  }, []);

  return (
    <main className="section">
      <div className="card" style={{ maxWidth: 520, margin: "0 auto" }}>
        <h1>Continue to GiveCampus</h1>
        <p className="muted">
          Gifts for Oregon Men&apos;s Rugby are processed by the University of Oregon on GiveCampus.
        </p>
        <a className="btn" href={GIVECAMPUS_DONATE_URL}>
          Open the official donation form
        </a>
      </div>
    </main>
  );
}
