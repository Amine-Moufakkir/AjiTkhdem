export interface User {
  id: string;
  email: string;
  name: string;
  skills: string[];
  preferenceLocation: string;
  preferenceSalary: number; // e.g. 120 (for $120k)
  preferenceJobType: 'Full-time' | 'Contract' | 'Part-time';
  preferenceWorkModel: 'Remote' | 'Hybrid' | 'On-site';
  subscriptionStatus: 'Free' | 'Pro';
  experience: ExperienceItem[];
  profileOptimizationScore: number;
  cvScore?: number;
  cvRecommendations?: string[];
  cvFileName?: string;
}

export interface ExperienceItem {
  id: string;
  title: string;
  company: string;
  type: string;
  period: string; // e.g. "Jan 2021 - Present"
  description: string;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  companyLogo: string;
  location: string;
  salaryMin: number; // e.g. 140
  salaryMax: number; // e.g. 180
  type: 'Full-time' | 'Contract' | 'Part-time';
  workModel: 'Remote' | 'Hybrid' | 'On-site';
  description: string;
  responsibilities: string[];
  requirements: string[];
  industry: string;
  companySize: string;
  website: string;
}

export interface JobMatch {
  jobId: string;
  score: number;
  reasons: {
    skills: string; // e.g. "Your skills match 3 out of 5 required skills (Figma, Design Systems)"
    location: string; // e.g. "Perfect location alignment (Remote match)"
    salary: string; // e.g. "$140k is above your minimum target of $120k"
    jobType: string; // e.g. "Matching job type (Full-time)"
  };
}

export interface JobApplication {
  id: string;
  jobId: string;
  appliedAt: string;
  status: 'applied' | 'pending';
}

export interface DashboardStats {
  autoAppliedCount: number;
  interviewsSecured: number;
  profileViews: number;
  alignmentScore: number;
}

export interface AuthResponse {
  user: User;
  message: string;
}
