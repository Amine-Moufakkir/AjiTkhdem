import React from 'react';
import { 
  LayoutDashboard, 
  Briefcase, 
  User, 
  CreditCard, 
  Settings, 
  Rocket, 
  Sparkles,
  LogOut
} from 'lucide-react';
import { User as UserType } from '../types.js';

interface SideNavBarProps {
  user: UserType;
  currentTab: string;
  onTabChange: (tab: string) => void;
  onUpgrade: () => void;
  onLogout: () => void;
}

export default function SideNavBar({ 
  user, 
  currentTab, 
  onTabChange, 
  onUpgrade, 
  onLogout 
}: SideNavBarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'jobs', label: 'Jobs', icon: Briefcase },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'billing', label: 'Billing', icon: CreditCard },
  ];

  return (
    <aside id="side-navigation" className="bg-surface-container-low border-r border-outline-variant flex flex-col w-64 h-full shrink-0">
      {/* Brand Logo */}
      <div className="h-16 flex items-center px-6 border-b border-outline-variant/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shadow-sm">
            <Sparkles className="w-5 h-5 text-on-primary fill-current" />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
            AutoApply AI
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-4 flex flex-col gap-1 overflow-y-auto">
        {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`flex items-center gap-3 px-4 py-2 mx-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'bg-primary-container text-on-primary-container shadow-sm font-semibold'
                  : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-primary' : 'text-on-surface-variant'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* User Area & CTA */}
      <div className="p-4 border-t border-outline-variant/55 mt-auto">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary/20 to-secondary/20 text-primary flex items-center justify-center font-bold text-sm border border-outline-variant/50">
            {user.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-semibold text-on-surface truncate">{user.name}</span>
            <span className={`text-xs px-2 py-0.5 mt-0.5 rounded-full self-start font-bold uppercase tracking-wider ${
              user.subscriptionStatus === 'Pro' 
                ? 'bg-secondary/10 text-secondary border border-secondary/20' 
                : 'bg-on-surface-variant/10 text-on-surface-variant'
            }`}>
              {user.subscriptionStatus} Plan
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          {user.subscriptionStatus === 'Free' && (
            <button
              onClick={onUpgrade}
              className="w-full bg-gradient-to-r from-primary to-secondary text-on-primary hover:opacity-90 transition-opacity rounded-lg py-2 text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
            >
              <Rocket className="w-3.5 h-3.5" />
              Upgrade to AI Pro
            </button>
          )}
          
          <button
            onClick={onLogout}
            className="w-full bg-transparent text-on-surface-variant hover:text-error hover:bg-error-container/10 border border-outline-variant rounded-lg py-2 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
}
