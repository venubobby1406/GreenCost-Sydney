import { cn } from '@/lib/utils';

/** Horizontal rule with an optional inline label. */
export default function Separator({
  label,
  className,
}: {
  label?: string;
  className?: string;
}) {
  if (!label) return <hr className={cn('ui-separator', className)} />;
  return (
    <div className={cn('ui-separator-labelled', className)} role="separator" aria-label={label}>
      <span className="ui-separator-rule" />
      <span className="ui-separator-text">{label}</span>
      <span className="ui-separator-rule" />
    </div>
  );
}
