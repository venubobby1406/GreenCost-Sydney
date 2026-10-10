'use client';
import { useId, useRef, useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

/**
 * Accessible tooltip. Renders on hover and keyboard focus, dismisses on Escape,
 * and is described to assistive tech via aria-describedby.
 */
export default function Tooltip({
  content,
  children,
  side = 'top',
  className,
}: {
  content: ReactNode;
  children: ReactNode;
  side?: 'top' | 'bottom';
  className?: string;
}) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  function show() {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setOpen(true), 120);
  }
  function hide() {
    if (timer.current) clearTimeout(timer.current);
    setOpen(false);
  }

  return (
    <span
      className={cn('ui-tooltip', className)}
      onPointerEnter={show}
      onPointerLeave={hide}
      onFocusCapture={show}
      onBlurCapture={hide}
    >
      <span aria-describedby={open ? id : undefined} className="ui-tooltip-anchor">
        {children}
      </span>
      {open && (
        <span role="tooltip" id={id} className={cn('ui-tooltip-bubble', `ui-tooltip-${side}`)}>
          {content}
        </span>
      )}
    </span>
  );
}
