'use client';
import { useRef, useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

/**
 * Scrollable region with styled scrollbars and edge fades that appear only when
 * there is more content in that direction.
 */
export default function ScrollArea({
  children,
  className,
  maxHeight = 420,
  label,
}: {
  children: ReactNode;
  className?: string;
  maxHeight?: number | string;
  label?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [atTop, setAtTop] = useState(true);
  const [atBottom, setAtBottom] = useState(true);

  function measure() {
    const node = ref.current;
    if (!node) return;
    setAtTop(node.scrollTop <= 2);
    setAtBottom(node.scrollTop + node.clientHeight >= node.scrollHeight - 2);
  }

  return (
    <div className={cn('ui-scroll-area', !atTop && 'is-scrolled-top', !atBottom && 'is-scrolled-bottom', className)}>
      <div
        ref={ref}
        onScroll={measure}
        className="ui-scroll-viewport"
        style={{ maxHeight }}
        tabIndex={0}
        role={label ? 'region' : undefined}
        aria-label={label}
      >
        {children}
      </div>
    </div>
  );
}
