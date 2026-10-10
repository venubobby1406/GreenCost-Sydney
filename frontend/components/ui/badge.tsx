import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

const TONES = {
  neutral: 'ui-badge-neutral',
  accent: 'ui-badge-accent',
  success: 'ui-badge-success',
  warning: 'ui-badge-warning',
  danger: 'ui-badge-danger',
} as const;

export type BadgeTone = keyof typeof TONES;

/** Compact status pill. `title` keeps the full status readable on hover. */
export default function Badge({
  children,
  tone = 'neutral',
  icon,
  className,
  title,
}: {
  children: ReactNode;
  tone?: BadgeTone;
  icon?: ReactNode;
  className?: string;
  title?: string;
}) {
  return (
    <span className={cn('ui-badge', TONES[tone], className)} title={title}>
      {icon}
      {children}
    </span>
  );
}
