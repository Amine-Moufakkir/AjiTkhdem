import React from 'react';
import { 
  Rocket, 
  ArrowRight, 
  Sparkles, 
  Briefcase, 
  UserCheck, 
  Eye, 
  Percent, 
  Building2, 
  MapPin, 
  DollarSign,
  FileText,
  UploadCloud
} from 'lucide-react';
import { User, Job, DashboardStats } from '../types.js';

interface DashboardViewProps {
  user: User;
  stats: DashboardStats | null;
  jobs: (Job & { match: any; applied: boolean })[];
  onTabChange: (tab: string) => void;
  onJobSelect: (jobId: string) => void;
  onUpgrade: () => void;
  onQuickApply: (jobId: string) => void;
}

export default function DashboardView({
  user,
  stats,
  jobs,
  onTabChange,
  onJobSelect,
  onUpgrade,
  onQuickApply
}: DashboardViewProps) {
  // Take top 3 highest matches as suggested core items
  const recommendations = jobs.slice(0, 3);

  // Fallback default stats if none loaded
  const displayStats = stats || {
    autoAppliedCount: 2,
    interviewsSecured: 1,
    profileViews: 145,
    alignmentScore: 94
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-on-surface">
            Welcome back, {user.name.split(' ')[0]}.
          </h1>
          <p className="text-on-surface-variant text-base mt-1">
            Here is your career intelligence overview for today.
          </p>
        </div>
        <button
          onClick={() => onTabChange('jobs')}
          className="bg-gradient-to-r from-primary to-secondary text-on-primary rounded-xl px-4 py-2.5 flex items-center gap-2 text-sm font-semibold shadow-sm hover:opacity-90 transition-opacity cursor-pointer"
        >
          <Sparkles className="w-4 h-4 fill-current" />
          AutoApply to Top Matches
        </button>
      </header>

      {/* Bento Grid Analytics */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* CV Quality Score & Recommendations (Span 8) */}
        <div className="md:col-span-8 flex flex-col gap-6">
          {user.cvFileName ? (
            <>
              <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 flex flex-col sm:flex-row items-center justify-between gap-6 hover:shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-shadow">
                <div className="flex-1 space-y-2">
                  <h3 className="text-lg font-bold text-on-surface">Score de qualité globale du CV</h3>
                  <p className="text-sm text-on-surface-variant leading-relaxed max-w-md">
                    Analyse complétée pour votre fichier : <strong className="text-primary break-all">{user.cvFileName}</strong>.
                    Ce score évalue l'intégrité structurelle, l'harmonie du formalisme et l'attractivité générale auprès des recruteurs.
                  </p>
                </div>
                <div className="flex flex-col items-center justify-center w-32 h-32 rounded-full border-4 border-primary-container relative shrink-0 bg-primary/5">
                  <span className="text-3xl font-extrabold text-primary">{user.cvScore !== undefined ? user.cvScore : 85}%</span>
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider text-center px-1">Qualité CV</span>
                </div>
              </div>

              {/* CV Suggestions Section */}
              <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 space-y-4 hover:shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-shadow">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-secondary fill-current shrink-0" />
                  <h3 className="text-base font-bold text-on-surface">Suggestions d'amélioration de la clarté</h3>
                </div>
                
                <div className="grid grid-cols-1 gap-3">
                  {((user.cvRecommendations && user.cvRecommendations.length > 0) 
                    ? user.cvRecommendations 
                    : [
                        "Ajouter de la quantification sur vos livrables professionnels récents pour rassurer le recruteur.",
                        "Structurer l'en-tête en plaçant vos coordonnées bien en évidence avec un titre métier percutant.",
                        "Optimiser les espacements horizontaux afin d'aérer la lecture globale du document."
                      ]
                  ).map((rec, i) => (
                    <div key={i} className="flex gap-3 items-start bg-surface-container-high/20 p-3 rounded-lg border border-outline-variant/25">
                      <span className="bg-primary/10 text-primary w-5.5 h-5.5 rounded-full flex items-center justify-center text-xs font-black shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <p className="text-xs md:text-sm text-on-surface-variant leading-relaxed font-medium">{rec}</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-8 flex flex-col items-center justify-center text-center gap-5 hover:shadow-[0_4px_16px_rgba(0,0,0,0.04)] transition-shadow">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <FileText className="w-8 h-8" />
              </div>
              <div className="max-w-md space-y-2">
                <h3 className="text-lg font-bold text-on-surface">Ajoutez votre CV pour avoir un score et des suggestions</h3>
                <p className="text-sm text-on-surface-variant leading-relaxed">
                  Importez votre CV au format PDF à tout moment. L'IA Gemini l'évaluera et vous fournira instantanément des suggestions constructives et personnalisées pour maximiser votre taux d'impact auprès des recruteurs !
                </p>
              </div>
              <button
                onClick={() => onTabChange('profile')}
                className="bg-primary hover:bg-primary-dim text-on-primary rounded-xl px-5 py-2.5 flex items-center gap-2 text-xs sm:text-sm font-semibold shadow-sm transition-opacity cursor-pointer"
              >
                <UploadCloud className="w-4 h-4" />
                Importer mon CV (PDF)
              </button>
            </div>
          )}

          {/* Freemium CTA Banner if user is Free */}
          {user.subscriptionStatus === 'Free' ? (
            <div className="bg-surface-container-high rounded-xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4 border border-outline-variant">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container">
                  <Rocket className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-on-surface">Unlock Unlimited Matching</h4>
                  <p className="text-xs text-on-surface-variant">Go Pro for boundless AI application matches, automated CV preparation, and priority routing.</p>
                </div>
              </div>
              <button
                onClick={onUpgrade}
                className="bg-on-surface text-surface hover:bg-inverse-surface rounded-lg px-4 py-2 text-xs font-bold transition-colors cursor-pointer"
              >
                Upgrade Now
              </button>
            </div>
          ) : (
            <div className="bg-gradient-to-r from-primary/10 to-secondary/10 border-l-4 border-l-secondary rounded-r-xl rounded-l-md p-5 flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-secondary shrink-0" />
              <div>
                <h4 className="text-sm font-bold text-on-surface">Pro Subscription Active</h4>
                <p className="text-xs text-on-surface-variant">Your automated AI agent is actively tracking matching opportunities for your specified core competencies.</p>
              </div>
            </div>
          )}
        </div>

        {/* Activity Summary Stats (Span 4) */}
        <div className="md:col-span-4 bg-surface-container-lowest border border-outline-variant rounded-xl p-6 flex flex-col justify-between hover:shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-shadow">
          <h3 className="text-base font-bold text-on-surface">Weekly Activity</h3>
          <div className="space-y-4 mt-4">
            <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
              <span className="text-sm text-on-surface-variant flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-primary" /> Auto-Applied
              </span>
              <strong className="text-sm text-on-surface">{displayStats.autoAppliedCount}</strong>
            </div>
            <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
              <span className="text-sm text-on-surface-variant flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-tertiary" /> Interviews Secured
              </span>
              <strong className="text-sm text-tertiary">{displayStats.interviewsSecured}</strong>
            </div>
            <div className="flex justify-between items-center pb-1">
              <span className="text-sm text-on-surface-variant flex items-center gap-2">
                <Eye className="w-4 h-4 text-secondary" /> Profile Views
              </span>
              <strong className="text-sm text-on-surface">{displayStats.profileViews}</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Top AI Recommendations */}
      <section className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-bold text-on-surface">Top AI Recommendations</h3>
          <button
            onClick={() => onTabChange('jobs')}
            className="text-sm font-semibold text-primary hover:underline flex items-center gap-1 cursor-pointer"
          >
            View all listings <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {recommendations.length === 0 ? (
          <div className="bg-surface-container-low border border-outline-variant rounded-xl p-10 text-center">
            <Briefcase className="w-10 h-10 text-on-surface-variant/40 mx-auto mb-2" />
            <p className="text-sm text-on-surface-variant">Aucune offre d'emploi recommandée pour le moment. Veuillez mettre à jour vos Profils d'intérêt dans l'onglet Profil pour déclencher de nouvelles correspondances.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendations.map(job => (
              <div
                key={job.id}
                onClick={() => onJobSelect(job.id)}
                className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 hover:border-primary/50 cursor-pointer overflow-hidden relative group hover:shadow-[0_4px_16px_rgba(0,0,0,0.06)] transition-all flex flex-col justify-between"
              >
                {/* Rule-based AI left-accent border */}
                <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-primary to-secondary op-80"></div>
                
                <div>
                  <div className="flex justify-between items-start mb-3">
                    <div className="w-10 h-10 bg-surface-container rounded-lg flex items-center justify-center border border-outline-variant/30">
                      {job.companyLogo ? (
                        <img src={job.companyLogo} alt={job.company} className="w-full h-full object-contain p-1.5 rounded" />
                      ) : (
                        <Building2 className="w-5 h-5 text-primary" />
                      )}
                    </div>
                    <span className="bg-secondary/10 border border-secondary/20 text-secondary text-xs font-bold px-2 py-1 rounded-md flex items-center gap-0.5">
                      <Sparkles className="w-3 h-3 fill-current" /> {job.match.score}% Match
                    </span>
                  </div>

                  <h4 className="text-[17px] font-bold text-on-surface mb-1 group-hover:text-primary transition-colors line-clamp-1">{job.title}</h4>
                  <p className="text-xs text-on-surface-variant mb-4">{job.company} • {job.location}</p>

                  <div className="flex flex-wrap gap-1.5 mb-6">
                    <span className="bg-surface-container text-on-surface-variant text-[10px] font-semibold px-2 py-0.5 rounded flex items-center gap-0.5">
                      <MapPin className="w-3 h-3" /> {job.workModel}
                    </span>
                    <span className="bg-surface-container text-on-surface-variant text-[10px] font-semibold px-2 py-0.5 rounded flex items-center gap-0.5">
                      <DollarSign className="w-3 h-3" /> {job.salaryMin}k - {job.salaryMax}k
                    </span>
                  </div>
                </div>

                <div 
                  onClick={(e) => {
                    e.stopPropagation(); // Stop parent bubble trigger
                    if (job.applied) return;
                    onQuickApply(job.id);
                  }}
                >
                  <button 
                    disabled={job.applied}
                    className={`w-full py-2 rounded-lg text-xs font-bold border transition-colors cursor-pointer ${
                      job.applied
                        ? 'bg-surface-container text-on-surface-variant/70 border-outline-variant/40 cursor-default'
                        : 'border-primary text-primary hover:bg-primary hover:text-on-primary'
                    }`}
                  >
                    {job.applied ? 'Already Applied' : 'Quick Apply'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
