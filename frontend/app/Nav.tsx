"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { clearToken, getToken } from "@/lib/api";
import { GIVECAMPUS_DONATE_URL } from "@/lib/donate";

export default function Nav() {
  const [authed, setAuthed] = useState(false);
  useEffect(() => setAuthed(Boolean(getToken())), []);

  return (
    <nav className="nav">
      <Link className="brand" href="/">
        <img className="mark" src="/uo-rugby-logo.png?v=4" alt="Oregon Men's Rugby" />
        Oregon Men&apos;s Rugby
      </Link>
      <div className="nav-links">
        <Link href="/#team">The Club</Link>
        <a href={GIVECAMPUS_DONATE_URL}>Donate</a>
        {authed ? (
          <>
            <Link href="/dashboard">Player hub</Link>
            <button
              className="btn ghost"
              onClick={() => {
                clearToken();
                window.location.href = "/";
              }}
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <Link href="/login">Player log in</Link>
            <Link className="btn" href="/signup">
              Player sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
