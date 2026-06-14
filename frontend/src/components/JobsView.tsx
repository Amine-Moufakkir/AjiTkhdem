import React, { useState, useMemo } from 'react';
import { 
  Building2, 
  MapPin, 
  DollarSign, 
  Sparkles, 
  ArrowRight, 
  Search, 
  SlidersHorizontal,
  Bookmark
} from 'lucide-react';
import { Job, User } from '../types.js';

interface JobsViewProps {
  user: User;
  jobs: (Job & { match: any; applied: boolean })[];
  onJobSelect: (jobId: string) => void;
  onQuickApply: (jobId: string) => void;
}

export default function JobsView({
  user,
  jobs,
  onJobSelect,
  onQuickApply
}: JobsViewProps) {
  // Local Filter States
  const [searchLocation, setSearchLocation] = useState('');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['Full-time']);
  const [minSalary, setMinSalary] = useState(100); // Default $100k
  const [sortBy, setSortBy] = useState<'match' | 'salary'>('match');

  const handleTypeChange = (type: string) => {
    if (selectedTypes.includes(type)) {
      setSelectedTypes(selectedTypes.filter(t => t !== type));
    } else {
      setSelectedTypes([...selectedTypes, type]);
    }
  };

  const handleClearFilters = () => {
    setSearchLocation('');
    setRemoteOnly(false);
    setSelectedTypes(['Full-time', 'Contract', 'Part-time']);
    setMinSalary(50);
  };

  // Filter & Sort Logic
  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      // 1. Location text match
      if (searchLocation && !job.location.toLowerCase().includes(searchLocation.toLowerCase())) {
        return false;
      }

      // 2. Remote Only filter
      if (remoteOnly && job.workModel !== 'Remote' && !job.location.toLowerCase().includes('remote')) {
        return false;
      }

      // 3. Job Type matching (match if selectedTypes array contains job.type, or if none selected)
      if (selectedTypes.length > 0 && !selectedTypes.includes(job.type)) {
        return false;
      }

      // 4. Minimum Salary matching
      if (job.salaryMax < minSalary) {
        return false;
      }

      return true;
    }).sort((a, b) => {
      if (sortBy === 'salary') {
        return b.salaryMax - a.salaryMax;
      }
      return b.match.score - a.match.score;
    });
  }, [jobs, searchLocation, remoteOnly, selectedTypes, minSalary, sortBy]);

  return (
    <div className="flex flex-col lg:flex-row h-full gap-6 animate-fade-in">
      {/* Side Filters (Hidden on small screens, sidebar layout) */}
      <aside className="w-full lg:w-72 bg-surface-container-low border border-outline-variant/60 rounded-xl p-5 shrink-0 flex flex-col gap-6">
        <div className="border-b border-outline-variant/50 pb-3 flex justify-between items-center">
          <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
            <SlidersHorizontal className="w-5 h-5 text-primary" /> Filters
          </h2>
          <button 
            onClick={handleClearFilters}
            className="text-xs text-on-surface-variant hover:text-primary font-medium cursor-pointer"
          >
            Clear all
          </button>
        </div>

        {/* Location Filter */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-on-surface uppercase tracking-wider block">Location</label>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant/70" />
            <input
              type="text"
              value={searchLocation}
              onChange={(e) => setSearchLocation(e.target.value)}
              placeholder="City, state, or remote"
              className="w-full pl-9 pr-3 py-2 bg-surface-container-lowest border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg text-sm transition-colors outline-none placeholder:text-on-surface-variant/50"
            />
          </div>
          <div className="mt-2">
            <label className="flex items-center gap-2 cursor-pointer group">
              <input
                type="checkbox"
                checked={remoteOnly}
                onChange={(e) => setRemoteOnly(e.target.checked)}
                className="rounded border-outline-variant text-primary focus:ring-primary h-4 w-4"
              />
              <span className="text-xs text-on-surface-variant group-hover:text-on-surface transition-colors font-medium">Remote Only</span>
            </label>
          </div>
        </div>

        {/* Job Type Filter */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-on-surface uppercase tracking-wider block">Job Type</label>
          <div className="flex flex-col gap-2.5">
            {['Full-time', 'Contract', 'Part-time'].map(type => (
              <label key={type} className="flex items-center gap-2.5 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={selectedTypes.includes(type)}
                  onChange={() => handleTypeChange(type)}
                  className="rounded border-outline-variant text-primary focus:ring-primary h-4 w-4"
                />
                <span className="text-sm text-on-surface-variant group-hover:text-on-surface transition-colors font-medium">{type}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Salary Slider Filter */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-on-surface uppercase tracking-wider block">Minimum Salary</label>
          <div className="px-1">
            <input
              type="range"
              min="50"
              max="250"
              step="10"
              value={minSalary}
              onChange={(e) => setMinSalary(Number(e.target.value))}
              className="w-full h-1 bg-outline-variant rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div className="flex justify-between mt-2 text-xs text-on-surface-variant font-medium">
              <span>$50k</span>
              <span className="text-primary font-bold">${minSalary}k+</span>
              <span>$250k</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Jobs Listing Canvas */}
      <div className="flex-1 space-y-6">
        {/* Recommended Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/30 pb-4">
          <div>
            <h1 className="text-2xl font-bold text-on-surface tracking-tight">Recommended for you</h1>
            <p className="text-sm text-on-surface-variant">
              Based on your user profile. Surfacing the highest probability match listings.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-on-surface-variant font-bold uppercase tracking-wider shrink-0">Sort By:</label>
            <select
              value={sortBy}
              onChange={(e: any) => setSortBy(e.target.value)}
              className="bg-surface-container-lowest border border-outline-variant px-3 py-1.5 rounded-lg text-xs font-bold text-on-surface focus:outline-none cursor-pointer"
            >
              <option value="match">Match Score</option>
              <option value="salary">Highest Salary</option>
            </select>
          </div>
        </div>

        {/* Job Recommendations Cards list */}
        {filteredJobs.length === 0 ? (
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-12 text-center">
            <SlidersHorizontal className="w-12 h-12 text-on-surface-variant/30 mx-auto mb-3 animate-pulse" />
            <h3 className="text-base font-bold text-on-surface">No Match Found</h3>
            <p className="text-sm text-on-surface-variant mt-1">No vacancies comply with your selected query metrics. Modify ranges to explore adjacent roles.</p>
            <button
              onClick={handleClearFilters}
              className="mt-4 bg-primary text-on-primary px-4 py-2 rounded-lg text-xs font-bold"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-12">
            {filteredJobs.map(job => (
              <article
                key={job.id}
                onClick={() => onJobSelect(job.id)}
                className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 relative overflow-hidden group hover:shadow-[0_8px_24px_rgba(0,0,0,0.06)] hover:border-primary/50 transition-all duration-350 flex flex-col justify-between cursor-pointer"
              >
                {/* Highlight Badge side border */}
                <div className={`absolute top-0 left-0 w-1.5 h-full ${
                  job.match.score >= 90
                    ? 'bg-gradient-to-b from-primary to-secondary opacity-90'
                    : 'bg-primary'
                }`}></div>

                <div>
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-lg bg-surface-container flex items-center justify-center p-1 border border-outline-variant/30 shrink-0">
                        {job.companyLogo ? (
                          <img src={job.companyLogo} alt={job.company} className="w-full h-full object-contain p-1 rounded" />
                        ) : (
                          <Building2 className="w-6 h-6 text-primary" />
                        )}
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-on-surface group-hover:text-primary transition-colors line-clamp-1">{job.title}</h3>
                        <p className="text-xs text-on-surface-variant">{job.company} • {job.location}</p>
                      </div>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                      }} 
                      className="text-on-surface-variant/60 hover:text-primary transition-colors p-1"
                    >
                      <Bookmark className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Core tags */}
                  <div className="flex flex-wrap gap-1.5 mb-5">
                    <span className="bg-surface-container text-on-surface-variant px-2.5 py-1 rounded-full text-[10px] font-semibold border border-outline-variant/30 flex items-center gap-0.5">
                      <MapPin className="w-3 h-3" /> {job.workModel}
                    </span>
                    <span className="bg-surface-container text-on-surface-variant px-2.5 py-1 rounded-full text-[10px] font-semibold border border-outline-variant/30 flex items-center gap-0.5">
                      <DollarSign className="w-3 h-3" /> {job.salaryMin}k - {job.salaryMax}k
                    </span>
                    <span className="bg-surface-container text-on-surface-variant px-2.5 py-1 rounded-full text-[10px] font-semibold border border-outline-variant/30">
                      {job.type}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-outline-variant/20 pt-4.5 mt-auto">
                  {/* AI Match Badge */}
                  <div className="flex items-center gap-1.5 bg-gradient-to-r from-primary/10 to-secondary/10 px-3 py-1.5 rounded-full border border-primary/15">
                    <Sparkles className="w-3.5 h-3.5 text-secondary fill-current" />
                    <span className="text-xs font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
                      {job.match.score}% Match
                    </span>
                  </div>

                  <div 
                    onClick={(e) => {
                      e.stopPropagation();
                      if (job.applied) return;
                      onQuickApply(job.id);
                    }}
                  >
                    <button
                      disabled={job.applied}
                      className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-colors cursor-pointer ${
                        job.applied
                          ? 'bg-surface-container text-on-surface-variant/70 border-none cursor-default'
                          : 'bg-primary text-on-primary hover:bg-surface-tint'
                      }`}
                    >
                      {job.applied ? 'Applied' : 'Apply Now'}
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
