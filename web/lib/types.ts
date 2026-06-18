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
