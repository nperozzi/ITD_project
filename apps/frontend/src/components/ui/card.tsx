import type { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export type CardProps = HTMLAttributes<HTMLDivElement>;

export function Card({ className, ...props }: CardProps): JSX.Element {
  return <div className={cn('rounded-lg border border-border bg-card p-4 text-card-foreground', className)} {...props} />;
}