import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "AtlasAI — Grounded Knowledge",
  description: "Enterprise knowledge search with grounded, cited answers.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
