"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export default function SignupPage() {
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      const res = await api<{ verification_hint?: string | null }>("/auth/signup", {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password"),
          full_name: form.get("full_name"),
          jersey_number: form.get("jersey_number") || null,
          position: form.get("position") || null,
        }),
      });
      setOk(
        res.verification_hint
          ? `SendGrid is not configured yet, so use this confirmation link: ${res.verification_hint}`
          : "Check your Duck ID inbox and confirm the @uoregon.edu link to finish signup.",
      );
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <main className="section">
      <div className="card" style={{ maxWidth: 520, margin: "0 auto" }}>
        <h1>Player sign up</h1>
        <p className="muted">Accounts are limited to University of Oregon emails ending in @uoregon.edu.</p>
        <form onSubmit={onSubmit}>
          <label>Full name</label>
          <input name="full_name" required />
          <label>Duck ID email</label>
          <input name="email" type="email" required placeholder="you@uoregon.edu" />
          <label>Password</label>
          <input name="password" type="password" minLength={8} required />
          <label>Jersey number</label>
          <input name="jersey_number" />
          <label>Position</label>
          <input name="position" placeholder="Hooker, fly-half…" />
          {error && <p className="error">{error}</p>}
          {ok && <p className="ok">{ok}</p>}
          <button className="btn" type="submit">
            Create account
          </button>
        </form>
      </div>
    </main>
  );
}
