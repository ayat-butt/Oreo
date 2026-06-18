// Entity × employment-type matrix — mirrors CONTRACT_PAIRS in the backend engine.
export const ENTITIES = [
  { value: "opl", label: "OPL — Orenda (Pvt) Ltd" },
  { value: "owt", label: "OWT — Orenda Welfare Trust" },
  { value: "taleemabad", label: "Taleemabad Inc — senior leadership only" },
  { value: "orenda", label: "Orenda — Addendum (extension)" },
];

export const PAIRS: Record<string, string[]> = {
  owt: ["full_time", "project", "part_time"],
  opl: ["full_time", "project", "part_time"],
  taleemabad: ["full_time", "project", "part_time"],
  orenda: ["addendum"],
};

export const TYPE_LABELS: Record<string, string> = {
  full_time: "Full-time",
  project: "Project",
  part_time: "Part-time",
  addendum: "Addendum",
};

export const ALLOWED_CC_DOMAINS = ["taleemabad.com", "niete.edu.pk", "niete.pk"];

export function ccDomainOk(email: string): boolean {
  const d = email.trim().toLowerCase().split("@")[1] ?? "";
  return ALLOWED_CC_DOMAINS.includes(d);
}
