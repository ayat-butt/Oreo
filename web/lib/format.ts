const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

/** "2026-07-01" → "1 July 2026" (the display format the contract engine expects). */
export function toDisplayDate(iso: string): string {
  if (!iso) return "";
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return iso;
  return `${d} ${MONTHS[m - 1]} ${y}`;
}

export function maskCnic(c?: string | null): string {
  if (!c) return "—";
  const digits = c.replace(/\s/g, "");
  if (digits.length < 5) return "•••";
  return `${digits.slice(0, 3)}••••${digits.slice(-2)}`;
}
