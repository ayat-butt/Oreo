import type { Metadata } from "next";
import { Lato, EB_Garamond } from "next/font/google";
import "./globals.css";

const lato = Lato({
  subsets: ["latin"],
  weight: ["300", "400", "700"],
  variable: "--font-lato",
  display: "swap",
});

const ebGaramond = EB_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-eb-garamond",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Contracts Portal — Taleemabad",
  description: "Draft, review, and send employment contracts for the People & Culture team.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${lato.variable} ${ebGaramond.variable}`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
