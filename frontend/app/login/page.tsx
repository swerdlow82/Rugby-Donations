"use client";

import { FormEvent, useState } from "react";
import { api, setToken } from "@/lib/api";

export default function LoginPage() {
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      const res = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password"),
        }),
      });
      setToken(res.access_token);
      window.location.href = "/dashboard";
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <main className="section">
      <div className="card" style={{ maxWidth: 480, margin: "0 auto" }}>
        <h1>Player log in</h1>
        <form onSubmit={onSubmit}>
          <label>@uoregon.edu email</label>
          <input name="email" type="email" required />
          <label>Password</label>
          <input name="password" type="password" required />
          {error && <p className="error">{error}</p>}
          <button className="btn" type="submit">
            Log in
          </button>
        </form>
      </div>
    </main>
  );
}
