"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, setToken } from "@/lib/api";
import { Suspense } from "react";

function VerifyInner() {
  const params = useSearchParams();
  const [message, setMessage] = useState("Confirming your Duck ID…");

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      setMessage("Missing confirmation token.");
      return;
    }
    api<{ access_token: string }>(`/auth/verify/${token}`, { method: "POST" })
      .then((res) => {
        setToken(res.access_token);
        setMessage("Email confirmed. Taking you to the player hub…");
        window.location.href = "/dashboard";
      })
      .catch((e) => setMessage(e.message));
  }, [params]);

  return (
    <main className="section">
      <div className="card" style={{ maxWidth: 480, margin: "0 auto" }}>
        <h1>Verify email</h1>
        <p>{message}</p>
      </div>
    </main>
  );
}

export default function VerifyPage() {
  return (
    <Suspense>
      <VerifyInner />
    </Suspense>
  );
}
