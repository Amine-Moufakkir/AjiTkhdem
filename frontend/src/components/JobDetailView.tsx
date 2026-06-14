import React, { useState } from 'react';
import { 
  ArrowLeft, 
  Sparkles, 
  MapPin, 
  DollarSign, 
  Building2, 
  Calendar, 
  Send, 
  Check, 
  Globe, 
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import { Job, User } from '../types.js';

interface JobDetailViewProps {
  user: User;
  job: (Job & { match: any; applied: boolean }) | null;
  onBack: () => void;
  onApply: (jobId: string) => void;
  adjacentJobs: (Job & { match: any })[];
  onJobSelect: (jobId: string) => void;
}

export default function JobDetailView({
  user,
  job,
  onBack,
  onApply,
  adjacentJobs,
  onJobSelect
}: JobDetailViewProps) {
  const [submitting, setSubmitting] = useState(false);

  if (!job) {
    return (
      <div className="p-8 text-center bg-surface-container-low rounded-xl border border-outline-variant">
        <p className="text-on-surface-variant font-medium">Job listing details failed to load.</p>
        <button onClick={onBack} className="mt-4 text-primary font-bold flex items-center justify-center gap-2 mx-auto">
          <ArrowLeft className="w-4 h-4" /> Go Back
        </button>
      </div>
    );
  }

  const handleApplyClick = async () => {
    setSubmitting(true);
    try {
      await onApply(job.id);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Top Breadcrumb Nav */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm font-semibold text-on-surface-variant hover:text-primary transition-colors cursor-pointer group"
      >
        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" /> Back to Listings
      </button>

      {/* Main Grid: Info + AI Matching column */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left main: Header, Details, Tasks (Span 8) */}
        <div className="lg:col-span-8 bg-surface-container-lowest border border-outline-variant rounded-xl p-6 space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start gap-4 pb-6 border-b border-outline-variant/30">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-surface-container flex items-center justify-center border border-outline-variant/40 shrink-0">
                {job.companyLogo ? (
                  <img src={job.companyLogo} alt={job.company} className="w-full h-full object-contain p-1 rounded" />
                ) : (
                  <Building2 className="w-8 h-8 text-primary" />
                )}
              </div>
              <div>
                <h1 className="text-2xl font-bold text-on-surface tracking-tight">{job.title}</h1>
                <p className="text-sm text-on-surface-variant font-medium mt-0.5 flex flex-wrap items-center gap-2">
                  <span className="text-on-surface font-semibold">{job.company}</span>
                  <span>•</span>
                  <span>{job.location}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 bg-gradient-to-r from-primary/10 to-secondary/10 px-3 py-1.5 rounded-full border border-primary/20 shrink-0">
              <Sparkles className="w-4 h-4 text-secondary fill-current animate-pulse" />
              <span className="text-sm font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
                {job.match.score}% Core Align
              </span>
            </div>
          </div>

          {/* Quick Meta parameters */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-surface-container/30 rounded-xl">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant block">Target Salary</span>
              <span className="text-sm font-bold text-on-surface">${job.salaryMin}k - ${job.salaryMax}k</span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant block">Work Model</span>
              <span className="text-sm font-bold text-on-surface">{job.workModel}</span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant block">Job Type</span>
              <span className="text-sm font-bold text-on-surface">{job.type}</span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-on-surface-variant block">Sector</span>
              <span className="text-sm font-bold text-on-surface">{job.industry}</span>
            </div>
          </div>

          {/* Job description */}
          <div className="space-y-2">
            <h3 className="text-lg font-bold text-on-surface">Role Overview</h3>
            <p className="text-sm text-on-surface-variant leading-relaxed">{job.description}</p>
          </div>

          {/* Key responsibilities */}
          <div className="space-y-3.5">
            <h3 className="text-lg font-bold text-on-surface">Core Responsibilities</h3>
            <ul className="space-y-2.5">
              {job.responsibilities.map((resp, i) => (
                <li key={i} className="flex gap-2.5 text-sm text-on-surface-variant leading-relaxed">
                  <span className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0 font-bold text-xs mt-0.5">
                    {i+1}
                  </span>
                  <span>{resp}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Requirements list */}
          <div className="space-y-3.5">
            <h3 className="text-lg font-bold text-on-surface">Experience &amp; Competencies</h3>
            <ul className="space-y-2.5">
              {job.requirements.map((req, i) => (
                <li key={i} className="flex gap-2.5 text-sm text-on-surface-variant leading-relaxed">
                  <Check className="w-4 h-4 text-secondary shrink-0 mt-0.5" />
                  <span>{req}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right main: AI Match panel + Action Center (Span 4) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Action Card center */}
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 space-y-4">
            <h3 className="text-base font-bold text-on-surface">Application Center</h3>

            {job.applied ? (
              <div className="space-y-3">
                <div className="bg-green-100/60 text-green-800 border border-green-200 p-4.5 rounded-lg flex items-center gap-3">
                  <ShieldCheck className="w-5 h-5 text-green-700 shrink-0" />
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider">Already Submitted</h4>
                    <p className="text-[11px] mt-0.5">AI dynamic agent completed auto-routing for this vacancy.</p>
                  </div>
                </div>
                <div className="flex gap-2 text-xs text-on-surface-variant/70 text-center font-medium px-1">
                  <span>Open: Ongoing interview routing</span>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Freemium Limit warning banner for Free plan users */}
                {user.subscriptionStatus === 'Free' && (
                  <div className="bg-amber-100/60 border border-amber-200 rounded-lg p-3.5 flex gap-2.5 items-start">
                    <AlertTriangle className="w-4.5 h-4.5 text-amber-700 shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-xs font-bold text-amber-900 leading-tight">Freemium Account Plan</h4>
                      <p className="text-[10px] text-amber-800 mt-0.5 leading-normal">
                        Your free tier profile is limited to 2 submissions. Upgrade to Pro for unlimited AI automatic route matches.
                      </p>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleApplyClick}
                  disabled={submitting}
                  className="w-full bg-primary hover:bg-surface-tint text-on-primary font-bold py-3 px-4 rounded-lg text-sm flex items-center justify-center gap-2 shrink-0 cursor-pointer shadow-sm transition-colors"
                >
                  <Send className="w-4 h-4" />
                  {submitting ? 'Submitting Application...' : 'Apply with AutoApply AI'}
                </button>

                <a
                  href={`https://${job.website}`}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full bg-transparent border border-outline-variant hover:bg-surface-container-low text-on-surface-variant font-bold py-2.5 px-4 rounded-lg text-xs flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Globe className="w-3.5 h-3.5" /> Visit Company Website <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>

          {/* AI Match Reasons Explanatory Panel */}
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 space-y-4">
            <h3 className="text-base font-bold text-on-surface flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-secondary fill-current" /> Why this job matches you
            </h3>
            
            <p className="text-xs text-on-surface-variant">
              AutoApply AI analyzed the parameters of this opportunity against your live target criteria:
            </p>

            <div className="space-y-4 pt-2">
              {/* Skills overlap Reason */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-on-surface">Core Competencies</span>
                  <span className="font-semibold text-primary">Match 40%</span>
                </div>
                <p className="text-[11px] text-on-surface-variant/85 leading-normal bg-surface-container/30 border border-outline-variant/20 p-2 rounded">
                  {job.match.reasons.skills}
                </p>
              </div>

              {/* Location Reason */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-on-surface">Work Model Fit</span>
                  <span className="font-semibold text-secondary">Match 20%</span>
                </div>
                <p className="text-[11px] text-on-surface-variant/85 leading-normal bg-surface-container/30 border border-outline-variant/20 p-2 rounded">
                  {job.match.reasons.location}
                </p>
              </div>

              {/* Salary Reason */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-on-surface">Target Salary compatibility</span>
                  <span className="font-semibold text-tertiary">Match 20%</span>
                </div>
                <p className="text-[11px] text-on-surface-variant/85 leading-normal bg-surface-container/30 border border-outline-variant/20 p-2 rounded">
                  {job.match.reasons.salary}
                </p>
              </div>

              {/* Job Type Reason */}
              <div className="space-y-1">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-on-surface">Job contract type</span>
                  <span className="font-semibold text-on-surface">Match 20%</span>
                </div>
                <p className="text-[11px] text-on-surface-variant/85 leading-normal bg-surface-container/30 border border-outline-variant/20 p-2 rounded">
                  {job.match.reasons.jobType}
                </p>
              </div>
            </div>
          </div>

          {/* Adjacent Roles recommendations */}
          {adjacentJobs.length > 0 && (
            <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-on-surface">Adjacent Aligned Openings</h3>
              <div className="space-y-2">
                {adjacentJobs.map(adj => (
                  <div
                    key={adj.id}
                    onClick={() => onJobSelect(adj.id)}
                    className="flex justify-between items-center p-2 rounded-lg hover:bg-surface-container/40 border border-transparent hover:border-outline-variant/20 cursor-pointer transition-all"
                  >
                    <div>
                      <h4 className="text-xs font-bold text-on-surface line-clamp-1">{adj.title}</h4>
                      <p className="text-[10px] text-on-surface-variant">{adj.company}</p>
                    </div>
                    <span className="text-[11px] font-bold text-secondary text-right">{adj.match.score}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
