import React, { useState } from 'react';
import { 
  Check, 
  Rocket, 
  Sparkles, 
  AlertTriangle, 
  CreditCard,
  History,
  ShieldCheck,
  CheckCircle2
} from 'lucide-react';
import { User } from '../types.js';

interface BillingViewProps {
  user: User;
  onUpgrade: () => Promise<void>;
  onDowngrade: () => Promise<void>;
}

export default function BillingView({ user, onUpgrade, onDowngrade }: BillingViewProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [feedback, setFeedback] = useState('');

  const handleUpgrade = async () => {
    setLoading('upgrade');
    setFeedback('');
    try {
      await onUpgrade();
      setFeedback('Subscription updated successfully! Pro Tier features unlocked.');
    } catch {
      setFeedback('Upgrade failed. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const handleDowngrade = async () => {
    setLoading('downgrade');
    setFeedback('');
    try {
      await onDowngrade();
      setFeedback('Subscription canceled successfully. Reverted to Free plan.');
    } catch {
      setFeedback('Failed to cancel subscription.');
    } finally {
      setLoading(null);
    }
  };

  const isPro = user.subscriptionStatus === 'Pro';

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Top Header */}
      <header>
        <h1 className="text-2xl font-bold text-on-surface tracking-tight">Billing &amp; Subscription plans</h1>
        <p className="text-sm text-on-surface-variant">
          Empower your job hunt with state-of-the-art AI auto-routing limits. Select a tier aligned with your velocity requirements.
        </p>
      </header>

      {feedback && (
        <div className="bg-primary-container text-on-primary-container p-4 rounded-xl border border-primary/20 text-xs font-semibold max-w-xl">
          {feedback}
        </div>
      )}

      {/* Pricing Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl">
        {/* Free Plan Card */}
        <div className={`bg-surface-container-lowest border rounded-xl p-6 flex flex-col justify-between relative overflow-hidden transition-all duration-300 hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)] ${
          !isPro ? 'border-primary shadow-sm' : 'border-outline-variant/60'
        }`}>
          {!isPro && (
            <span className="absolute top-0 right-0 bg-primary text-on-primary font-bold text-[10px] px-3 py-1 rounded-bl-xl uppercase tracking-wider">
              Active Tier
            </span>
          )}

          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-bold text-on-surface">Standard Free</h3>
              <p className="text-xs text-on-surface-variant">Basic discovery search for passive jobseekers.</p>
            </div>
            
            <div className="flex items-baseline gap-1 py-1.5">
              <span className="text-4xl font-extrabold text-on-surface">$0</span>
              <span className="text-xs text-on-surface-variant font-medium">/ month</span>
            </div>

            <ul className="space-y-2.5 pt-2">
              <li className="flex gap-2.5 items-start text-xs text-on-surface-variant leading-relaxed">
                <Check className="w-4 h-4 text-primary shrink-0" />
                <span>Deterministic Match calculations</span>
              </li>
              <li className="flex gap-2.5 items-start text-xs text-on-surface-variant leading-relaxed">
                <Check className="w-4 h-4 text-primary shrink-0" />
                <span>Limit: Up to 2 automated applications</span>
              </li>
              <li className="flex gap-2.5 items-start text-[11px] text-on-surface-variant/40 line-through leading-relaxed">
                <Check className="w-3.5 h-3.5 shrink-0" />
                <span>Unlimited concurrent auto-apply tracking</span>
              </li>
              <li className="flex gap-2.5 items-start text-[11px] text-on-surface-variant/40 line-through leading-relaxed">
                <Check className="w-3.5 h-3.5 shrink-0" />
                <span>Resumes compilation builder integrations</span>
              </li>
            </ul>
          </div>

          <div className="pt-6 mt-6 border-t border-outline-variant/20">
            {!isPro ? (
              <button
                disabled
                className="w-full bg-surface-container text-on-surface-variant/70 border border-transparent rounded-lg py-2.5 text-xs font-bold leading-normal text-center cursor-default"
              >
                Current Active Tier
              </button>
            ) : (
              <button
                onClick={handleDowngrade}
                disabled={loading !== null}
                className="w-full bg-transparent text-on-surface-variant hover:bg-surface-container border border-outline-variant rounded-lg py-2.5 text-xs font-bold cursor-pointer transition-colors"
              >
                {loading === 'downgrade' ? 'Reverting plan...' : 'Downgrade to Standard Free'}
              </button>
            )}
          </div>
        </div>

        {/* AI Pro Plan Card */}
        <div className={`bg-surface-container-lowest border rounded-xl p-6 flex flex-col justify-between relative overflow-hidden transition-all duration-300 hover:shadow-[0_8px_24px_rgba(0,0,0,0.06)] ${
          isPro ? 'border-secondary shadow-sm ring-1 ring-secondary/25' : 'border-outline-variant/60'
        }`}>
          {isPro && (
            <span className="absolute top-0 right-0 bg-secondary text-on-secondary font-bold text-[10px] px-3 py-1 rounded-bl-xl uppercase tracking-wider">
              Active Tier
            </span>
          )}

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-on-surface flex items-center gap-1">
                  AI Pro <Sparkles className="w-4.5 h-4.5 text-secondary fill-current" />
                </h3>
                <p className="text-xs text-on-surface-variant">Our premier autonomous application solution.</p>
              </div>
            </div>

            <div className="flex items-baseline gap-1 py-1.5">
              <span className="text-4xl font-extrabold text-on-surface">$29</span>
              <span className="text-xs text-on-surface-variant font-medium">/ month</span>
            </div>

            <ul className="space-y-2.5 pt-2">
              <li className="flex gap-2.5 items-start text-xs text-on-surface-variant leading-relaxed">
                <CheckCircle2 className="w-4 h-4 text-secondary shrink-0 fill-secondary/15" />
                <span className="text-on-surface font-semibold">Priority matching routing score optimization</span>
              </li>
              <li className="flex gap-2.5 items-start text-xs text-on-surface-variant leading-relaxed">
                <CheckCircle2 className="w-4 h-4 text-secondary shrink-0 fill-secondary/15" />
                <span className="text-on-surface font-semibold">Unlimited automatic applications</span>
              </li>
              <li className="flex gap-2.5 items-start text-xs text-on-surface-variant leading-relaxed">
                <CheckCircle2 className="w-4 h-4 text-secondary shrink-0 fill-secondary/15" />
                <span>Smart customized cover letter auto-compiles</span>
              </li>
              <li className="flex gap-2.5 items-start text-xs text-on-surface-variant leading-relaxed">
                <CheckCircle2 className="w-4 h-4 text-secondary shrink-0 fill-secondary/15" />
                <span>Dedicated client operations dashboard</span>
              </li>
            </ul>
          </div>

          <div className="pt-6 mt-6 border-t border-outline-variant/20">
            {isPro ? (
              <button
                disabled
                className="w-full bg-surface-container text-on-surface-variant/70 border border-transparent rounded-lg py-2.5 text-xs font-bold leading-normal text-center cursor-default"
              >
                AI Pro Plan Active
              </button>
            ) : (
              <button
                onClick={handleUpgrade}
                disabled={loading !== null}
                className="w-full bg-gradient-to-r from-primary to-secondary text-on-primary hover:opacity-90 rounded-lg py-2.5 text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm cursor-pointer transition-opacity"
              >
                <Rocket className="w-3.5 h-3.5" />
                {loading === 'upgrade' ? 'Upgrading tier...' : 'Upgrade instantly for $29'}
              </button>
            )}
          </div>
        </div>
      </section>

      {/* COMPARISON TIER MATRIX TABLE */}
      <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 space-y-4 max-w-4xl">
        <h3 className="text-base font-bold text-on-surface">Plan Comparison Table</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-outline-variant/40 pb-2">
                <th className="py-2.5 text-on-surface-variant/70 font-bold uppercase tracking-wider">Features</th>
                <th className="py-2.5 text-on-surface-variant/70 font-bold uppercase tracking-wider text-center w-28">Standard</th>
                <th className="py-2.5 text-on-surface-variant/70 font-bold uppercase tracking-wider text-center w-28">AI Pro</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              <tr>
                <td className="py-3 text-on-surface font-semibold text-xs leading-normal">Deterministic AI scoring matchers</td>
                <td className="py-3 text-center"><Check className="w-4 h-4 text-primary mx-auto" /></td>
                <td className="py-3 text-center"><Check className="w-4 h-4 text-secondary mx-auto" /></td>
              </tr>
              <tr>
                <td className="py-3 text-on-surface font-semibold text-xs leading-normal">Cover letter &amp; CV customization</td>
                <td className="py-3 text-center text-on-surface-variant/40">-</td>
                <td className="py-3 text-center"><Check className="w-4 h-4 text-secondary mx-auto" /></td>
              </tr>
              <tr>
                <td className="py-3 text-on-surface font-semibold text-xs leading-normal">Automated job tracking limits</td>
                <td className="py-3 text-center text-on-surface font-bold">2 max</td>
                <td className="py-3 text-center text-secondary font-bold">Unlimited</td>
              </tr>
              <tr>
                <td className="py-3 text-on-surface font-semibold text-xs leading-normal">Priority system job routing</td>
                <td className="py-3 text-center text-on-surface-variant/40">-</td>
                <td className="py-3 text-center"><Check className="w-4 h-4 text-secondary mx-auto" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Transaction History Simulation */}
      <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-6 space-y-4 max-w-4xl">
        <h3 className="text-base font-bold text-on-surface flex items-center gap-2">
          <History className="w-5 h-5 text-primary" /> Historic Payments Ledger
        </h3>

        <div className="space-y-2 text-xs">
          <div className="flex justify-between items-center p-3 hover:bg-surface-container-high/40 rounded-lg border border-outline-variant/20">
            <div className="flex items-center gap-3">
              <CreditCard className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
              <div>
                <p className="font-semibold text-on-surface">AutoApply AI Premium Renewal</p>
                <p className="text-[10px] text-on-surface-variant">Jun 01, 2026 • Vis Card ending in 4242</p>
              </div>
            </div>
            <div className="text-right">
              <span className="font-bold text-on-surface">{isPro ? '$29.00' : '$0.00'}</span>
              <span className="text-[10px] uppercase font-bold text-green-700 bg-green-150 px-2 py-0.5 rounded-full block mt-0.5 border border-green-200/50">Settled</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
