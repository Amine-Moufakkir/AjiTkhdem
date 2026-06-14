import React, { useState } from 'react';
import { Sparkles, Shield, Mail, Lock, User, Rocket, CheckCircle2 } from 'lucide-react';

interface LoginViewProps {
  onLogin: (email: string, password: string) => Promise<void>;
  onRegister: (name: string, email: string, password: string) => Promise<void>;
}

export default function LoginView({ onLogin, onRegister }: LoginViewProps) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password || (isRegister && !name)) {
      setError('Please provide all mandatory parameters.');
      return;
    }

    setLoading(true);
    try {
      if (isRegister) {
        await onRegister(name, email, password);
      } else {
        await onLogin(email, password);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication sequence failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    setLoading(true);
    try {
      const redirectUri = `${window.location.origin}/api/auth/google/callback`;
      const res = await fetch(`/api/auth/google/url?redirect_uri=${encodeURIComponent(redirectUri)}`);
      if (!res.ok) {
        throw new Error('Could not retrieve Google OAuth authorization link from backend.');
      }
      
      const { url } = await res.json();
      
      const width = 500;
      const height = 650;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;
      
      const authWindow = window.open(
        url,
        'google_oauth_popup',
        `width=${width},height=${height},top=${top},left=${left},scrollbars=yes,status=yes`
      );
      
      if (!authWindow) {
        setError('Popup blocker detected. Please enable popups for this site to sign in with Google.');
        setLoading(false);
        return;
      }
      
      const handlePopupMessage = (event: MessageEvent) => {
        const origin = event.origin;
        if (!origin.endsWith('.run.app') && !origin.includes('localhost')) {
          return;
        }
        if (event.data?.type === 'OAUTH_AUTH_FAILURE') {
          setError(decodeURIComponent(event.data.error || 'Google authorization aborted.'));
          setLoading(false);
          window.removeEventListener('message', handlePopupMessage);
        } else if (event.data?.type === 'OAUTH_AUTH_SUCCESS') {
          setLoading(false);
          window.removeEventListener('message', handlePopupMessage);
        }
      };
      
      window.addEventListener('message', handlePopupMessage);
      
      const checkClosedTimer = setInterval(() => {
        if (authWindow.closed) {
          clearInterval(checkClosedTimer);
          setLoading(false);
          window.removeEventListener('message', handlePopupMessage);
        }
      }, 1000);
      
    } catch (err: any) {
      setError(err.message || 'Connecting to Google OAuth backend failed.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-surface flex items-center justify-center p-4 md:p-8 animate-fade-in">
      <div className="w-full max-w-5xl bg-surface-container-lowest border border-outline-variant rounded-2xl overflow-hidden shadow-xl grid grid-cols-1 md:grid-cols-12 min-h-[600px]">
        
        {/* Left Columns: Features display layout (Span 5) */}
        <div className="md:col-span-5 bg-gradient-to-br from-primary to-secondary p-8 md:p-12 text-on-primary flex flex-col justify-between relative overflow-hidden">
          {/* Background overlay accent arcs */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-24 translate-x-24 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-24 -translate-x-24 pointer-events-none"></div>

          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 bg-white/10 px-3 py-1 rounded-full backdrop-blur-sm self-start border border-white/10">
              <Sparkles className="w-4 h-4 fill-current" />
              <span className="text-[11px] font-bold uppercase tracking-wider">AI Platform Engine</span>
            </div>
            <h2 className="text-3xl font-extrabold tracking-tight leading-tight pt-2">
              Automate your career trajectory.
            </h2>
            <p className="text-sm text-on-primary/80 leading-relaxed max-w-sm">
              Stop manually tracking spreadsheets. Let our autonomous matching daemon match and apply for vacancies that match your parameters.
            </p>
          </div>

          <div className="space-y-4 pt-8 border-t border-white/15">
            <div className="flex gap-3 items-start">
              <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold">Comprehensive Match Scorecard</h4>
                <p className="text-xs text-on-primary/75">Our deterministic matching scoring evaluates skills, location, salary, and workspace parameters.</p>
              </div>
            </div>
            <div className="flex gap-3 items-start">
              <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold">Secure JWT Authentication</h4>
                <p className="text-xs text-on-primary/75">Enterprise-grade HTTP-only cookies prevent token leakage mechanisms.</p>
              </div>
            </div>
          </div>

          <div className="text-xs text-on-primary/60 pt-6">
            © 2026 AutoApply AI Inc. All rights reserved.
          </div>
        </div>

        {/* Right Columns: Credentials inputs layout (Span 7) */}
        <div className="md:col-span-12 lg:col-span-7 p-8 md:p-12 flex flex-col justify-center bg-surface-container-lowest">
          <div className="max-w-md w-full mx-auto space-y-6">
            {/* Headers */}
            <div>
              <h1 className="text-2xl font-extrabold text-on-surface tracking-tight">
                {isRegister ? 'Create your career account' : 'Sign in to platform'}
              </h1>
              <p className="text-sm text-on-surface-variant mt-1.5 font-medium">
                {isRegister 
                  ? 'Get started on AutoApply AI in seconds.' 
                  : 'Welcome back. Access your personalized vacancy radar.'}
              </p>
            </div>

            {/* Error notifications */}
            {error && (
              <div id="login-error-summary" className="bg-error-container/20 text-error border border-error/25 p-3 rounded-lg text-xs font-semibold">
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4.5">
              {/* Optional Name field if Register */}
              {isRegister && (
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5" /> Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Alex Sterling"
                    className="w-full bg-surface-container-lowest border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2.5 text-sm text-on-surface outline-none transition-colors"
                  />
                </div>
              )}

              {/* Email field */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5" /> Email Address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex.sterling@example.com"
                  className="w-full bg-surface-container-lowest border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2.5 text-sm text-on-surface outline-none transition-colors"
                />
              </div>

              {/* Password field */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5" /> Password
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-surface-container-lowest border border-outline-variant focus:border-primary focus:ring-1 focus:ring-primary rounded-lg px-3 py-2.5 text-sm text-on-surface outline-none transition-colors"
                />
              </div>

              {/* Submit CTA */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary hover:bg-surface-tint text-on-primary font-bold py-3 rounded-lg text-xs shadow-md flex items-center justify-center gap-1.5 shrink-0 transition-opacity disabled:opacity-50 cursor-pointer mb-4"
              >
                <Rocket className="w-4 h-4" />
                {loading 
                  ? 'Authenticating details...' 
                  : isRegister 
                    ? 'Register profile & start matches' 
                    : 'Access Dashboard'}
              </button>

              {/* Divider layout section */}
              <div className="flex items-center my-4">
                <div className="flex-grow border-t border-outline-variant/35"></div>
                <span className="px-3 text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">or continue with</span>
                <div className="flex-grow border-t border-outline-variant/35"></div>
              </div>

              {/* Google OAuth Login Button */}
              <button
                type="button"
                onClick={handleGoogleSignIn}
                disabled={loading}
                className="w-full bg-surface-container-lowest hover:bg-surface-container-low text-on-surface border border-outline-variant font-bold py-3 rounded-lg text-xs shadow-sm flex items-center justify-center gap-2 transition-colors cursor-pointer disabled:opacity-50"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24" width="16" height="16" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                  <path d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z" fill="#FBBC05" />
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335" />
                </svg>
                {isRegister ? 'Sign up with Google' : 'Sign in with Google'}
              </button>
            </form>

            <div className="text-center border-t border-outline-variant/30 pt-6">
              <p className="text-xs text-on-surface-variant">
                {isRegister ? 'Already have an authenticated account?' : "Don't have an AutoApply AI profile?"}{' '}
                <button
                  type="button"
                  onClick={() => {
                    setIsRegister(!isRegister);
                    setError('');
                  }}
                  className="text-primary font-bold hover:underline"
                >
                  {isRegister ? 'Sign in instead' : 'Create profile free'}
                </button>
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
