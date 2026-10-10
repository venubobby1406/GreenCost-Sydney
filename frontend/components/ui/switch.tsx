'use client';
import { cn } from '@/lib/utils';

/** Accessible on/off switch. Renders a real checkbox so forms and labels keep working. */
export default function Switch({
  checked,
  onCheckedChange,
  label,
  disabled,
  className,
  id,
}: {
  checked: boolean;
  onCheckedChange: (next: boolean) => void;
  label: string;
  disabled?: boolean;
  className?: string;
  id?: string;
}) {
  return (
    <label className={cn('ui-switch', checked && 'is-on', disabled && 'is-disabled', className)}>
      <input
        id={id}
        type="checkbox"
        role="switch"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onCheckedChange(event.target.checked)}
      />
      <span className="ui-switch-track" aria-hidden="true">
        <span className="ui-switch-thumb" />
      </span>
      <span className="ui-switch-label">{label}</span>
    </label>
  );
}
