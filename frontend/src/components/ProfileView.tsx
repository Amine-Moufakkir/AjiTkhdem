import React, { useState } from 'react';
import { 
  User, 
  MapPin, 
  DollarSign, 
  Plus, 
  X, 
  Sparkles, 
  TrendingUp, 
  PlusCircle, 
  Trash2,
  Calendar,
  Building2,
  Bookmark,
  UploadCloud,
  FileText
} from 'lucide-react';
import { User as UserType, ExperienceItem } from '../types.js';

interface ProfileViewProps {
  user: UserType;
  onUpdateProfile: (updatedData: any) => Promise<void>;
  onCVUploaded: (updatedUser: UserType) => void;
}

export default function ProfileView({ user, onUpdateProfile, onCVUploaded }: ProfileViewProps) {
  // Configurable dynamic form inputs bonded to current API states
  const [name, setName] = useState(user.name);
  const [preferenceLocation, setPreferenceLocation] = useState(user.preferenceLocation);
  const [preferenceSalary, setPreferenceSalary] = useState(user.preferenceSalary);
  const [preferenceJobType, setPreferenceJobType] = useState(user.preferenceJobType);
  const [preferenceWorkModel, setPreferenceWorkModel] = useState(user.preferenceWorkModel);
  const [skills, setSkills] = useState<string[]>(user.skills);
  const [newSkill, setNewSkill] = useState('');
  
  // Custom experience lists
  const [experience, setExperience] = useState<ExperienceItem[]>(user.experience);
  const [newExpTitle, setNewExpTitle] = useState('');
  const [newExpCompany, setNewExpCompany] = useState('');
  const [newExpPeriod, setNewExpPeriod] = useState('');
  const [newExpDescription, setNewExpDescription] = useState('');
  const [showAddExp, setShowAddExp] = useState(false);

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const [uploading, setUploading] = useState(false);
  const [uploadStatusStep, setUploadStatusStep] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadError('Veuillez sélectionner un fichier PDF uniquement.');
      setUploadSuccess('');
      return;
    }

    setUploading(true);
    setUploadError('');
    setUploadSuccess('');
    setUploadStatusStep('Lecture du fichier PDF...');

    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        try {
          const base64String = event.target?.result as string;
          setUploadStatusStep('Extraction du texte & notation Gemini en cours...');
          
          const response = await fetch('/api/profile/upload-cv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              file: base64String,
              fileName: file.name
            })
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.error || "Une erreur est survenue lors de l'analyse.");
          }

          setUploadSuccess('Félicitations ! Votre CV a été analysé de manière globale avec succès. Votre score de CV et nos 3 axes d\'amélioration stratégiques ont été générés.');
          setUploadStatusStep('');
          onCVUploaded(data.user);
        } catch (err: any) {
          console.error(err);
          setUploadError(err.message || 'Une défaillance est survenue lors du traitement.');
        } finally {
          setUploading(false);
        }
      };
      
      reader.onerror = () => {
        setUploadError('Impossible de lire le fichier local.');
        setUploading(false);
      };

      reader.readAsDataURL(file);
    } catch (err: any) {
      setUploadError(err.message || 'Erreur lors du traitement.');
      setUploading(false);
    }
  };

  // Skill manipulations
  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      const updated = [...skills, newSkill.trim()];
      setSkills(updated);
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    const updated = skills.filter(s => s !== skillToRemove);
    setSkills(updated);
  };

  // Experience timeline manipulations
  const handleAddExperience = () => {
    if (!newExpTitle.trim() || !newExpCompany.trim() || !newExpPeriod.trim()) {
      return;
    }
    const newItem: ExperienceItem = {
      id: `exp-${Math.random().toString(36).substring(2, 9)}`,
      title: newExpTitle.trim(),
      company: newExpCompany.trim(),
      type: 'Full-time',
      period: newExpPeriod.trim(),
      description: newExpDescription.trim()
    };
    const updated = [...experience, newItem];
    setExperience(updated);
    setNewExpTitle('');
    setNewExpCompany('');
    setNewExpPeriod('');
    setNewExpDescription('');
    setShowAddExp(false);
  };

  const handleRemoveExperience = (expId: string) => {
    const updated = experience.filter(item => item.id !== expId);
    setExperience(updated);
  };

  // Dispatch profile updates
  const handleSaveProfile = async () => {
    setSaving(true);
    setMessage('');
    try {
      await onUpdateProfile({
        name,
        skills,
        preferenceLocation,
        preferenceSalary,
        preferenceJobType,
        preferenceWorkModel,
        experience
      });
      setMessage('Profile settings updated successfully!');
      setTimeout(() => setMessage(''), 4000);
    } catch (err: any) {
      setMessage(err.message || 'Failed to sync profile parameters.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in pb-12">
      {/* Profile Optimization Health (Left Span 8) */}
      <main className="lg:col-span-8 space-y-6">
        {/* Core demographic card */}
        <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 space-y-5">
          <h2 className="text-lg font-bold text-on-surface">Career Target Parameters</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Full Name */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Candidate Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-sm text-on-surface outline-none"
              />
            </div>

            {/* Target Location */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Target Geographic Preference</label>
              <input
                type="text"
                value={preferenceLocation}
                onChange={(e) => setPreferenceLocation(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-sm text-on-surface outline-none"
              />
            </div>

            {/* Preferred Work Model */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Preferred Work Structure</label>
              <select
                value={preferenceWorkModel}
                onChange={(e: any) => setPreferenceWorkModel(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface focus:border-primary outline-none cursor-pointer"
              >
                <option value="Remote">Remote Only</option>
                <option value="Hybrid">Hybrid</option>
                <option value="On-site">On-site Office</option>
              </select>
            </div>

            {/* Preferred Contract Type */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider">Desired Job Contract Classification</label>
              <select
                value={preferenceJobType}
                onChange={(e: any) => setPreferenceJobType(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface focus:border-primary outline-none cursor-pointer"
              >
                <option value="Full-time">Full-time Employee</option>
                <option value="Contract">Contract / Consultant</option>
                <option value="Part-time">Part-time</option>
              </select>
            </div>
          </div>

          {/* Preferred minimum annual salary block */}
          <div className="space-y-2 pt-2">
            <div className="flex justify-between items-center text-xs font-bold text-on-surface-variant uppercase tracking-wider">
              <span>Desired Minimum Annual Salary</span>
              <span className="text-primary font-extrabold text-sm">${preferenceSalary}k / year</span>
            </div>
            <input
              type="range"
              min="40"
              max="250"
              step="5"
              value={preferenceSalary}
              onChange={(e) => setPreferenceSalary(Number(e.target.value))}
              className="w-full h-1 bg-outline-variant rounded-lg appearance-none cursor-pointer accent-primary"
            />
          </div>
        </section>

        {/* Profils d'intérêt (Profiles of interest list tag block) */}
        <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 space-y-4">
          <div>
            <h3 className="text-lg font-bold text-on-surface">Profils d'intérêt recherchés</h3>
            <p className="text-xs text-on-surface-variant">
              Indiquez les profils ou types de postes pour lesquels vous êtes intéressé (ex : Développeur Fullstack, Product Manager, Data Analyst, Designer UI/UX). Ils seront analysés en recherche plein texte (Full-Text Search) et comparés via l'IA Gemini pour vous proposer des recommandations d'emploi sur mesure.
            </p>
          </div>

          {/* Interactive add tags block */}
          <form onSubmit={handleAddSkill} className="flex gap-2">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              placeholder="ex: Développeur Fullstack, Product Manager, Scrum Master, Data Scientist"
              className="flex-1 bg-surface-container-lowest border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2 text-sm text-on-surface outline-none"
            />
            <button
              type="submit"
              className="bg-primary hover:bg-surface-tint text-on-primary font-bold px-4 rounded-lg text-xs flex items-center gap-1 cursor-pointer transition-colors"
            >
              <Plus className="w-4 h-4" /> Ajouter un profil
            </button>
          </form>

          {/* Output Tag List */}
          {skills.length === 0 ? (
            <p className="text-xs text-on-surface-variant/70 italic text-center py-2">Aucun profil d'intérêt enregistré. Ajoutez au moins un profil pour calibrer vos recommandations.</p>
          ) : (
            <div className="flex flex-wrap gap-2 pt-2">
              {skills.map(skill => (
                <div
                  key={skill}
                  className="bg-surface-container text-on-surface font-semibold text-xs px-3 py-1.5 rounded-full border border-outline-variant/30 flex items-center gap-1.5 transition-colors hover:border-error/45 group hover:bg-surface-container-high"
                >
                  <span>{skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill)}
                    className="text-on-surface-variant group-hover:text-error transition-colors focus:outline-none"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Experience Timelines */}
        <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-on-surface">Experience Timeline</h3>
              <p className="text-xs text-on-surface-variant">Update your historical achievements to align target resumes.</p>
            </div>
            <button
              type="button"
              onClick={() => setShowAddExp(!showAddExp)}
              className="text-xs text-primary font-bold hover:underline flex items-center gap-1 cursor-pointer"
            >
              <PlusCircle className="w-4 h-4" /> Add Role
            </button>
          </div>

          {/* Add experience inputs */}
          {showAddExp && (
            <div className="bg-surface-container-high border border-outline-variant/50 rounded-xl p-4 space-y-3 animate-fade-in">
              <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface">Register Timeline Accomplishment</h4>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <input
                  type="text"
                  placeholder="Job Title"
                  value={newExpTitle}
                  onChange={(e) => setNewExpTitle(e.target.value)}
                  className="bg-surface-container-lowest border border-outline-variant rounded-lg px-2.5 py-1.5 text-xs text-on-surface outline-none"
                />
                <input
                  type="text"
                  placeholder="Company"
                  value={newExpCompany}
                  onChange={(e) => setNewExpCompany(e.target.value)}
                  className="bg-surface-container-lowest border border-outline-variant rounded-lg px-2.5 py-1.5 text-xs text-on-surface outline-none"
                />
                <input
                  type="text"
                  placeholder="Period (e.g. 2021 - Present)"
                  value={newExpPeriod}
                  onChange={(e) => setNewExpPeriod(e.target.value)}
                  className="bg-surface-container-lowest border border-outline-variant rounded-lg px-2.5 py-1.5 text-xs text-on-surface outline-none"
                />
              </div>

              <textarea
                placeholder="Highlight core accomplishments (e.g. Streamlined database requests by 40% using robust Redis parameters...)"
                rows={2}
                value={newExpDescription}
                onChange={(e) => setNewExpDescription(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg p-2.5 text-xs text-on-surface outline-none resize-none"
              ></textarea>

              <div className="flex justify-end gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setShowAddExp(false)}
                  className="px-3 py-1.5 text-on-surface-variant font-medium hover:bg-surface-container border border-outline-variant rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleAddExperience}
                  className="bg-primary text-on-primary font-bold px-3 py-1.5 rounded-lg"
                >
                  Save Accomplishment
                </button>
              </div>
            </div>
          )}

          {/* Render Timeline Experience list */}
          {experience.length === 0 ? (
            <p className="text-xs text-on-surface-variant/70 italic text-center py-4 border-2 border-dashed border-outline-variant/40 rounded-xl">No historical items registered.</p>
          ) : (
            <div className="relative border-l border-outline-variant/60 ml-3.5 pl-6 space-y-6">
              {experience.map(item => (
                <div key={item.id} className="relative group">
                  {/* Bullet center dot */}
                  <div className="absolute -left-[30px] top-1.5 w-3 h-3 rounded-full bg-primary ring-4 ring-primary-container"></div>
                  
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <h4 className="text-sm font-bold text-on-surface">{item.title}</h4>
                      <p className="text-xs text-on-surface-variant mt-0.5">{item.company} • <span className="font-medium text-[11px]">{item.period}</span></p>
                      {item.description && (
                        <p className="text-xs text-on-surface-variant/80 mt-1.5 leading-relaxed bg-surface-container/20 p-2 border border-outline-variant/20 rounded">
                          {item.description}
                        </p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveExperience(item.id)}
                      className="text-on-surface-variant hover:text-error hover:bg-error-container/10 p-1.5 rounded-lg transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Profile Optimization Score side widget (Right Span 4) */}
      <aside className="lg:col-span-4 space-y-6">
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 text-center flex flex-col items-center">
          <TrendingUp className="w-8 h-8 text-secondary mb-2" />
          <h3 className="text-base font-bold text-on-surface">Profile Optimization</h3>
          <p className="text-xs text-on-surface-variant mt-1">
            How complete and attractive your CV structure represents to corporate human recruiters.
          </p>

          <div className="relative w-32 h-32 flex items-center justify-center my-6">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              {/* Outer track circle */}
              <circle
                cx="50"
                cy="50"
                r="40"
                stroke="var(--color-outline-variant)"
                strokeWidth="6"
                fill="transparent"
                className="opacity-20"
              />
              {/* Inner active circle */}
              <circle
                cx="50"
                cy="50"
                r="40"
                stroke="var(--color-primary)"
                strokeWidth="6"
                fill="transparent"
                strokeDasharray={`${2 * Math.PI * 40}`}
                strokeDashoffset={`${2 * Math.PI * 40 * (1 - user.profileOptimizationScore / 100)}`}
                className="transition-all duration-500 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
              <span className="text-2xl font-black text-on-surface">{user.profileOptimizationScore}%</span>
              <span className="text-[9px] uppercase font-bold text-on-surface-variant">Profile Score</span>
            </div>
          </div>

          <div className="w-full text-left bg-surface-container-high/50 p-3 rounded-lg border border-outline-variant/40 space-y-2 text-xs text-on-surface-variant">
            <div className="flex items-center gap-2">
              <X className={`w-4 h-4 shrink-0 ${skills.length > 0 ? 'text-green-600' : 'text-on-surface-variant/40'}`} />
              <span className={skills.length > 0 ? 'line-through opacity-60' : ''}>Ajouter au moins 1 profil d'intérêt (+15%)</span>
            </div>
            <div className="flex items-center gap-2">
              <X className={`w-4 h-4 shrink-0 ${skills.length > 4 ? 'text-green-600' : 'text-on-surface-variant/40'}`} />
              <span className={skills.length > 4 ? 'line-through opacity-60' : ''}>Ajouter au moins 5 profils d'intérêt (+10%)</span>
            </div>
            <div className="flex items-center gap-2">
              <X className={`w-4 h-4 shrink-0 ${experience.length > 0 ? 'text-green-600' : 'text-on-surface-variant/40'}`} />
              <span className={experience.length > 0 ? 'line-through opacity-60' : ''}>Enregistrer l'historique d'expérience (+20%)</span>
            </div>
            <div className="flex items-center gap-2">
              <X className={`w-4 h-4 shrink-0 ${preferenceLocation && preferenceSalary ? 'text-green-600' : 'text-on-surface-variant/40'}`} />
              <span className={preferenceLocation && preferenceSalary ? 'line-through opacity-60' : ''}>Définir les critères de salaire & région (+15%)</span>
            </div>
          </div>
        </div>

        {/* CV Upload Module */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 space-y-4">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface">Importation du CV (PDF)</h4>
            <p className="text-xs text-on-surface-variant mt-1">
              Transmettez votre fichier PDF pour lancer l'analyse complète de sa qualité structurelle par l'IA Gemini.
            </p>
          </div>

          {user.cvFileName ? (
            <div className="flex items-start gap-2.5 text-xs bg-green-500/10 text-green-800 dark:text-green-400 p-3 rounded-lg border border-green-500/20">
              <FileText className="w-5 h-5 shrink-0 text-green-600 dark:text-green-400 mt-0.5" />
              <div className="space-y-1">
                <span className="font-semibold block break-all">Fichier actif : {user.cvFileName}</span>
                <span className="text-[10px] text-green-700 dark:text-green-500">
                  Qualité CV analysée ({user.cvScore !== undefined ? `${user.cvScore}/100` : "Calculé"})
                </span>
              </div>
            </div>
          ) : (
            <div className="text-xs text-on-surface-variant/70 italic bg-surface-container/30 px-3 py-2 rounded-lg border border-outline-variant/20 text-center">
              Aucun fichier de CV importé pour le moment.
            </div>
          )}

          <div className="relative">
            <input 
              type="file" 
              id="pdf-cv-file-uploader" 
              accept="application/pdf" 
              className="sr-only" 
              onChange={handleFileChange}
              disabled={uploading}
            />
            <label 
              htmlFor="pdf-cv-file-uploader"
              className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-6 text-center transition-colors cursor-pointer ${
                uploading 
                  ? 'border-primary/30 bg-primary/5 cursor-not-allowed'
                  : 'border-outline-variant hover:border-primary hover:bg-surface-container-low'
              }`}
            >
              <UploadCloud className={`w-8 h-8 mb-2 ${uploading ? 'text-primary animate-pulse' : 'text-on-surface-variant/60'}`} />
              <span className="text-xs font-bold text-on-surface block">
                {uploading ? "Traitement en cours..." : "Sélectionner ou Glisser le CV"}
              </span>
              <span className="text-[10px] text-on-surface-variant mt-0.5 block">Format PDF uniquement (Max. 15 Mo)</span>
            </label>
          </div>

          {uploading && (
            <div className="bg-primary/5 p-3 rounded-lg border border-primary/10 space-y-2">
              <div className="flex items-center gap-2 text-xs text-primary font-bold">
                <span className="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin"></span>
                <span>{uploadStatusStep}</span>
              </div>
              <div className="w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
                <div className="bg-primary h-full rounded-full animate-pulse" style={{ width: '70%' }}></div>
              </div>
            </div>
          )}

          {uploadError && (
            <div className="text-xs text-error bg-error-container/10 p-3 rounded-lg border border-error-container/20 font-medium">
              {uploadError}
            </div>
          )}

          {uploadSuccess && (
            <div className="text-xs text-green-800 bg-green-500/10 p-3 rounded-lg border border-green-500/20 leading-relaxed">
              {uploadSuccess}
            </div>
          )}
        </div>

        {/* Global Save Actions Widget */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 space-y-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-on-surface">Apply Changes</h4>
          <p className="text-xs text-on-surface-variant">
            Sync registered values with live AI recommendation endpoints to recalibrate alignment fits immediately.
          </p>

          {message && (
            <div className="bg-primary/10 border border-primary/20 text-primary p-3 rounded-lg text-xs font-semibold leading-relaxed">
              {message}
            </div>
          )}

          <button
            onClick={handleSaveProfile}
            disabled={saving}
            className="w-full bg-primary hover:bg-surface-tint text-on-primary font-bold py-2.5 rounded-lg text-xs cursor-pointer shadow-sm transition-colors text-center"
          >
            {saving ? 'Syncing Profile parameters...' : 'Update & Optimize Profile'}
          </button>
        </div>
      </aside>
    </div>
  );
}
