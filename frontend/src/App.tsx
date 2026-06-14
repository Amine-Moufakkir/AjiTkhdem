import React, { useState, useEffect } from 'react';
import { User, Job, DashboardStats } from './types.js';
import SideNavBar from './components/SideNavBar.js';
import DashboardView from './components/DashboardView.js';
import JobsView from './components/JobsView.js';
import JobDetailView from './components/JobDetailView.js';
import ProfileView from './components/ProfileView.js';
import BillingView from './components/BillingView.js';
import LoginView from './components/LoginView.js';

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [jobs, setJobs] = useState<(Job & { match: any; applied: boolean })[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  
  const [loading, setLoading] = useState<boolean>(true);

  // Authenticate helper called during boot and Google login callback matching
  const checkAuth = async () => {
    try {
      const res = await fetch('/api/auth/me');
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
        setCurrentTab('dashboard');
      }
    } catch (err) {
      console.error('Session authentication failed on boot:', err);
    } finally {
      setLoading(false);
    }
  };

  // Authenticate user on launch
  useEffect(() => {
    checkAuth();
  }, []);

  // Listen for Google Sign-In success messages from popup channel
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      const origin = event.origin;
      if (!origin.endsWith('.run.app') && !origin.includes('localhost')) {
        return;
      }
      if (event.data?.type === 'OAUTH_AUTH_SUCCESS') {
        checkAuth();
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Fetch contextual jobs & stats once logged in, or whenever preferences change
  useEffect(() => {
    if (!user) return;

    async function fetchPayloads() {
      try {
        // Envoie tous les profils d'intérêt saisis par l'utilisateur à l'API recommandée
        const [recsRes, statsRes] = await Promise.all([
          fetch('/api/recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profiles: user.skills })
          }),
          fetch('/api/dashboard/stats')
        ]);
        
        if (recsRes.ok) {
          const jobsData = await recsRes.json();
          setJobs(jobsData.jobs);
        } else {
          // Fallback resilient si l'API de recommandations personnalisées échoue
          const jobsRes = await fetch('/api/jobs');
          if (jobsRes.ok) {
            const jobsData = await jobsRes.json();
            setJobs(jobsData.jobs);
          }
        }

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData.stats);
        }
      } catch (err) {
        console.error('Failed to load backend payloads:', err);
      }
    }
    
    fetchPayloads();
  }, [user]);

  // Auth Handlers
  const handleLogin = async (email: string, password: string) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Login attempt failed.');
    }
    
    setUser(data.user);
    setCurrentTab('dashboard');
  };

  const handleRegister = async (name: string, email: string, password: string) => {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Registration failed.');
    }

    setUser(data.user);
    setCurrentTab('dashboard');
  };

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    setUser(null);
    setJobs([]);
    setStats(null);
    setCurrentTab('dashboard');
    setSelectedJobId(null);
  };

  // Profile updates
  const handleUpdateProfile = async (updatedData: any) => {
    const res = await fetch('/api/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedData)
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Failed to sync parameters.');
    }

    setUser(data.user);
  };

  // Subscriptions upgrade/downgrade
  const handleUpgrade = async () => {
    const res = await fetch('/api/billing/upgrade', { method: 'PUT' });
    const data = await res.json();
    if (res.ok) {
      setUser(data.user);
    }
  };

  const handleDowngrade = async () => {
    const res = await fetch('/api/billing/downgrade', { method: 'PUT' });
    const data = await res.json();
    if (res.ok) {
      setUser(data.user);
    }
  };

  // Quick Apply
  const handleApply = async (jobId: string) => {
    try {
      const res = await fetch(`/api/jobs/${jobId}/apply`, { method: 'POST' });
      const data = await res.json();
      
      if (!res.ok) {
        alert(data.message || 'Submission failed.');
        return;
      }

      // Re-trigger user stats & job applications tracking
      const [jobsRes, statsRes] = await Promise.all([
        fetch('/api/jobs'),
        fetch('/api/dashboard/stats')
      ]);
      
      if (jobsRes.ok) {
        const jobsData = await jobsRes.json();
        setJobs(jobsData.jobs);
      }
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData.stats);
      }

      alert('Application compiled and submitted successfully!');
    } catch (err) {
      console.error(err);
      alert('Error connecting with recruitment services.');
    }
  };

  // Navigation callbacks
  const handleTabChange = (tab: string) => {
    setCurrentTab(tab);
    setSelectedJobId(null); // Clear selected jobs when changing primary tabs
  };

  const handleJobSelect = (jobId: string) => {
    setCurrentTab('jobs');
    setSelectedJobId(jobId);
  };

  if (loading) {
    return (
      <div id="loader-canvas" className="min-h-screen bg-surface flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs text-on-surface-variant font-bold uppercase tracking-wider mt-4">Initializing career engine...</p>
      </div>
    );
  }

  // Not signed in -> render authentications dashboard
  if (!user) {
    return <LoginView onLogin={handleLogin} onRegister={handleRegister} />;
  }

  // Calculate matching details for selected detail layout
  const selectedJobDetail = selectedJobId ? jobs.find(j => j.id === selectedJobId) || null : null;
  // Calculate adjacent match vacancies (similar titles or same sector in other cards)
  const adjacentRoles = selectedJobDetail 
    ? jobs.filter(j => j.id !== selectedJobDetail.id && (j.industry === selectedJobDetail.industry || j.type === selectedJobDetail.type)).slice(0, 2)
    : [];

  return (
    <div className="flex h-screen bg-surface text-on-surface overflow-hidden">
      
      {/* Side Navigation panel */}
      <SideNavBar 
        user={user} 
        currentTab={currentTab} 
        onTabChange={handleTabChange} 
        onUpgrade={() => handleTabChange('billing')} 
        onLogout={handleLogout} 
      />

      {/* Main content canvas area */}
      <main className="flex-1 overflow-y-auto px-6 py-8 md:px-10">
        
        {currentTab === 'dashboard' && (
          <DashboardView 
            user={user} 
            stats={stats} 
            jobs={jobs} 
            onTabChange={handleTabChange} 
            onJobSelect={handleJobSelect} 
            onUpgrade={() => handleTabChange('billing')} 
            onQuickApply={handleApply} 
          />
        )}

        {currentTab === 'jobs' && (
          selectedJobId && selectedJobDetail ? (
            <JobDetailView 
              user={user} 
              job={selectedJobDetail} 
              onBack={() => setSelectedJobId(null)} 
              onApply={handleApply} 
              adjacentJobs={adjacentRoles} 
              onJobSelect={handleJobSelect} 
            />
          ) : (
            <JobsView 
              user={user} 
              jobs={jobs} 
              onJobSelect={handleJobSelect} 
              onQuickApply={handleApply} 
            />
          )
        )}

        {currentTab === 'profile' && (
          <ProfileView 
            user={user} 
            onUpdateProfile={handleUpdateProfile} 
            onCVUploaded={async (updatedUser) => {
              setUser(updatedUser);
              try {
                const res = await fetch('/api/dashboard/stats');
                if (res.ok) {
                  const data = await res.json();
                  setStats(data.stats);
                }
              } catch (err) {
                console.error("Failed to hot-reload dashboard stats:", err);
              }
            }}
          />
        )}

        {currentTab === 'billing' && (
          <BillingView 
            user={user} 
            onUpgrade={handleUpgrade} 
            onDowngrade={handleDowngrade} 
          />
        )}

      </main>
    </div>
  );
}
