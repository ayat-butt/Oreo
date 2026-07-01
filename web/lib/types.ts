export interface PipelineCandidate {
  application_id: number;
  candidate_id: number | null;
  job_id: number | null;
  name: string;
  email: string | null;
  department: string | null;
  job_title: string | null;
  status: string;            // offer | hired
  stage: string | null;
  ready_to_draft: boolean;
  cnic_present: boolean;
  job_employment_type: string | null;
  engine_employment_type: string | null;
  updated_at: string | null;
}

export interface DepartmentGroup {
  department: string;
  count: number;
  candidates: PipelineCandidate[];
}

export interface CandidatesResponse {
  total: number;
  ready_to_draft: number;
  groups: DepartmentGroup[];
}

// ── Email-sourced candidates (ingested from offer emails) ────────────────────
export interface EmailCandidate {
  id: string;
  name: string | null;
  role: string | null;
  department: string | null;
  personal_email: string | null;
  gross_salary: string | null;
  joining_date: string | null;
  status: string;              // new (needs review) | drafted | dismissed
  source_mailbox: string | null;
  sender: string | null;
  subject: string | null;
  received_at: string | null;
  created_at: string | null;
}

export interface EmailCandidatesResponse {
  total: number;
  needs_review: number;
  candidates: EmailCandidate[];
}

export interface AccessMember {
  id: string;
  email: string;
  name: string | null;
  is_admin: boolean;
  is_active: boolean;
  is_owner: boolean;
  created_at: string | null;
}

export interface AccessListResponse {
  members: AccessMember[];
}

export interface IngestResult {
  scanned: number;
  ingested: number;
  skipped_seen: number;
  skipped_not_offer: number;
  mailboxes: number;
  error?: string | null;
}
