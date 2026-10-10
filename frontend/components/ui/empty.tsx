import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

/** Illustrated empty state for regions that have no content yet. */
export default function Empty({
  icon,
  title,
  description,
  action,
  className,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('ui-empty', className)}>
      {icon && <span className="ui-empty-icon">{icon}</span>}
      <h3 className="ui-empty-title">{title}</h3>
      {description && <p className="ui-empty-text">{description}</p>}
      {action && <div className="ui-empty-action">{action}</div>}
    </div>
  );
}
