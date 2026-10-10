'use client';
import { cn } from '@/lib/utils';

/** Determinate progress bar with an accessible value. */
export default function Progress({
  value,
  label,
  className,
}: {
  value: number;
  label: string;
  className?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div
      className={cn('ui-progress', className)}
      role="progressbar"
      aria-label={label}
      aria-valuenow={Math.round(clamped)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <span className="ui-progress-fill" style={{ width: `${clamped}%` }} />
    </div>
  );
}
