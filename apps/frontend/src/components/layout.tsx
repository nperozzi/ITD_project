import type { ReactNode } from 'react';
import type { NavigationKey } from '../types';
import { cn } from '../lib/utils';

interface NavItem {
  key: NavigationKey;
  label: string;
}

interface AppLayoutProps {
  active: NavigationKey;
  onChange: (next: NavigationKey) => void;
  children: ReactNode;
}

const navItems: NavItem[] = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'stores', label: 'Stores' },
  { key: 'gateways', label: 'Gateways' },
  { key: 'shelf-locations', label: 'Shelf Locations' },
  { key: 'products', label: 'Products' },
  { key: 'tags', label: 'Tags' },
  { key: 'tag-payloads', label: 'Tag Payloads' },
  { key: 'promotions', label: 'Promotions' },
];

export function AppLayout({ active, onChange, children }: AppLayoutProps): JSX.Element {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-7xl gap-6 p-4 md:p-6">
      <aside className="w-64 rounded-xl border border-border bg-card p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Electronic Shelf Labels</p>
        <h1 className="mt-2 mb-5 text-lg font-semibold">Tag Management Console</h1>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <button
              key={item.key}
              onClick={() => onChange(item.key)}
              className={cn(
                'w-full rounded-md px-3 py-2 text-left text-sm font-medium transition-colors',
                active === item.key ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
              )}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="flex-1 space-y-4">
        <header className="rounded-xl border border-border bg-card px-5 py-4">
          <p className="text-sm text-muted-foreground">Customer workspace</p>
          <h2 className="text-xl font-semibold">Retail Operations</h2>
        </header>
        {children}
      </main>
    </div>
  );
}