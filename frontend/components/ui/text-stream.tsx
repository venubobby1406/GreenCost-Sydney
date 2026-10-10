'use client';
import { useEffect, useRef, useState } from 'react';
import { useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/utils';

/**
 * Reveals text progressively, like a model streaming a reply.
 * With reduced motion the full text is rendered immediately, so no information is gated.
 */
export default function TextStream({
  text,
  speed = 18,
  className,
  onDone,
}: {
  text: string;
  speed?: number;
  className?: string;
  onDone?: () => void;
}) {
  const reduced = useReducedMotion();
  const [shown, setShown] = useState(() => (reduced ? text.length : 0));
  const done = useRef(false);

  useEffect(() => {
    if (reduced) {
      setShown(text.length);
      return;
    }
    setShown(0);
    done.current = false;
    let frame = 0;
    const step = () => {
      frame = window.setTimeout(() => {
        setShown((n) => {
          if (n >= text.length) return n;
          return n + 2;
        });
      }, speed);
    };
    step();
    return () => window.clearTimeout(frame);
  }, [text, speed, reduced]);

  useEffect(() => {
    if (shown >= text.length && !done.current) {
      done.current = true;
      onDone?.();
    }
  }, [shown, text.length, onDone]);

  return (
    <span className={cn('ui-text-stream', className)} aria-label={text}>
      <span aria-hidden="true">{text.slice(0, shown)}</span>
      {/* Screen readers get the whole paragraph; sighted users see the reveal. */}
      <span className="ui-text-stream-sr">{text}</span>
    </span>
  );
}
