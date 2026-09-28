import type { Metadata } from "next";
import "./globals.css";
import Nav from "./Nav";

export const metadata: Metadata = {
  title: "Oregon Men's Rugby | Support the Ducks",
  description: "Donate to University of Oregon Men's Rugby and follow the season fundraising drive.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Source+Sans+3:wght@400;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Nav />
        {children}
        <footer className="footer">
          University of Oregon Men&apos;s Rugby Club · Student-run fundraising · Go Ducks
        </footer>
      </body>
    </html>
  );
}
