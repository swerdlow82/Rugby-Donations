"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, getToken } from "@/lib/api";

type Contact = { id?: number; name: string; value: string };
type Book = { emails: Contact[]; phones: Contact[] };
type Campaign = {
  id: number;
  subject: string;
  created_at: string;
  emails_sent: number;
  sms_sent: number;
  failed: number;
};

const emptyEmails = () => Array.from({ length: 20 }, () => ({ name: "", value: "" }));
const emptyPhones = () => Array.from({ length: 10 }, () => ({ name: "", value: "" }));

export default function DashboardPage() {
  const [me, setMe] = useState<{ full_name: string; email: string; is_verified: boolean } | null>(null);
  const [emails, setEmails] = useState<Contact[]>(emptyEmails());
  const [phones, setPhones] = useState<Contact[]>(emptyPhones());
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    api<{ full_name: string; email: string; is_verified: boolean }>("/auth/me")
      .then(setMe)
      .catch(() => {
        window.location.href = "/login";
      });
    api<Book>("/contacts").then((book) => {
      const e = emptyEmails();
      book.emails.forEach((c, i) => {
        if (i < 20) e[i] = { name: c.name, value: c.value };
      });
      const p = emptyPhones();
      book.phones.forEach((c, i) => {
        if (i < 10) p[i] = { name: c.name, value: c.value };
      });
      setEmails(e);
      setPhones(p);
    });
    api<Campaign[]>("/campaigns").then(setCampaigns).catch(() => undefined);
  }, []);

  function update(list: Contact[], setList: (c: Contact[]) => void, i: number, field: keyof Contact, value: string) {
    const next = [...list];
    next[i] = { ...next[i], [field]: value };
    setList(next);
  }

  async function saveContacts(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/contacts", {
        method: "PUT",
        body: JSON.stringify({
          emails: emails.filter((c) => c.value.trim()),
          phones: phones.filter((c) => c.value.trim()),
        }),
      });
      setMessage("Contact book saved (up to 20 emails and 10 numbers).");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function sendCampaign(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    const form = new FormData(e.currentTarget);
    try {
      const result = await api<Campaign>("/campaigns", {
        method: "POST",
        body: JSON.stringify({
          subject: form.get("subject"),
          email_body: form.get("email_body"),
          sms_body: form.get("sms_body"),
          send_email: form.get("send_email") === "on",
          send_sms: form.get("send_sms") === "on",
          confirmed_consent: form.get("confirmed_consent") === "on",
        }),
      });
      setCampaigns((c) => [result, ...c]);
      setMessage(
        `Sent ${result.emails_sent} emails and ${result.sms_sent} texts` +
          (result.failed ? ` (${result.failed} failed)` : "") +
          ". Without SendGrid/Twilio keys, messages are logged by the API instead of delivered.",
      );
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <main className="section">
      <h1>Player hub</h1>
      <p className="muted">
        {me ? `Signed in as ${me.full_name} · ${me.email}` : "Loading…"}
      </p>
      {error && <p className="error">{error}</p>}
      {message && <p className="ok">{message}</p>}

      <form className="card" onSubmit={saveContacts} style={{ marginTop: "1.2rem" }}>
        <h2>Family & friends contact book</h2>
        <p className="muted">20 email slots and 10 phone slots. Save people who already know you and expect this ask.</p>
        <h3>Emails</h3>
        {emails.map((c, i) => (
          <div className="row" key={`e-${i}`}>
            <input
              placeholder={`Name ${i + 1}`}
              value={c.name}
              onChange={(e) => update(emails, setEmails, i, "name", e.target.value)}
            />
            <input
              placeholder="email@example.com"
              value={c.value}
              onChange={(e) => update(emails, setEmails, i, "value", e.target.value)}
            />
          </div>
        ))}
        <h3>Phone numbers</h3>
        {phones.map((c, i) => (
          <div className="row" key={`p-${i}`}>
            <input
              placeholder={`Name ${i + 1}`}
              value={c.name}
              onChange={(e) => update(phones, setPhones, i, "name", e.target.value)}
            />
            <input
              placeholder="541-555-0100"
              value={c.value}
              onChange={(e) => update(phones, setPhones, i, "value", e.target.value)}
            />
          </div>
        ))}
        <button className="btn" type="submit">
          Save contacts
        </button>
      </form>

      <form className="card" onSubmit={sendCampaign} style={{ marginTop: "1.2rem" }}>
        <h2>Send a custom ask</h2>
        <p className="muted">
          Use {"{player_name}"}, {"{contact_name}"}, and {"{donate_link}"} in your message.
        </p>
        <label>Email subject</label>
        <input name="subject" defaultValue="Support Oregon Men's Rugby this season" required />
        <label>Email body</label>
        <textarea
          name="email_body"
          rows={6}
          required
          defaultValue={`Hi {contact_name},\n\nIt's {player_name} from University of Oregon Men's Rugby. We're raising travel and kit money for the season. Gifts go through the university on GiveCampus: {donate_link}\n\nGo Ducks,\n{player_name}`}
        />
        <label>Text message</label>
        <textarea
          name="sms_body"
          rows={4}
          required
          defaultValue={`Hi {contact_name}, it's {player_name} with Oregon Rugby. Official donate link: {donate_link}`}
        />
        <label>
          <input type="checkbox" name="send_email" defaultChecked /> Send emails
        </label>
        <label>
          <input type="checkbox" name="send_sms" defaultChecked /> Send texts
        </label>
        <label>
          <input type="checkbox" name="confirmed_consent" required /> I only listed people who know me and agreed to get this fundraising message.
        </label>
        <button className="btn" type="submit">
          Send now
        </button>
      </form>

      <div className="card" style={{ marginTop: "1.2rem" }}>
        <h2>Past sends</h2>
        {campaigns.length ? (
          <table>
            <thead>
              <tr>
                <th>Subject</th>
                <th>Emails</th>
                <th>Texts</th>
                <th>Failed</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c) => (
                <tr key={c.id}>
                  <td>{c.subject}</td>
                  <td>{c.emails_sent}</td>
                  <td>{c.sms_sent}</td>
                  <td>{c.failed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">No campaigns yet.</p>
        )}
      </div>
    </main>
  );
}
