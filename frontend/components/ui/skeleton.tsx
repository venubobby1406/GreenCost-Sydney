'use client';
import { cn } from '@/lib/utils';

/** Shimmer placeholder for loading regions. Keeps layout height stable. */
export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('ui-skeleton', className)} aria-hidden="true" {...props} />;
}

/** A stack of skeleton lines, sized to read like the content it replaces. */
export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn('ui-skeleton-text', className)} role="status" aria-label="Loading">
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton key={i} className={i === lines - 1 && lines > 1 ? 'ui-skeleton-line-short' : 'ui-skeleton-line'} />
      ))}
    </div>
  );
}
