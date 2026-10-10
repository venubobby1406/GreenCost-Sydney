'use client';
import { useEffect, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { CheckCircle2, X } from 'lucide-react';

export type Notice = { message: string; id: number };

/**
 * Transcription notification. Auto-dismisses after 6s with a visible countdown.
 * Reduced-motion users get an instant, static toast.
 */
export default function Toast({ notice, onDismiss }: { notice: Notice | null; onDismiss: () => void }) {
  const reduced = useReducedMotion();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!notice) return;
    setOpen(true);
    const timer = setTimeout(() => {
      setOpen(false);
      // Let the exit finish before clearing state.
      setTimeout(onDismiss, reduced ? 0 : 180);
    }, 6000);
    return () => clearTimeout(timer);
  }, [notice, onDismiss, reduced]);

  if (!notice) return null;

  const close = () => {
    setOpen(false);
    setTimeout(onDismiss, reduced ? 0 : 180);
  };

  return (
    <div className="toast-layer" aria-live="polite" role="status">
      <AnimatePresence>
        {open && (
          <motion.div
            key={notice.id}
            className="toast"
            initial={reduced ? { opacity: 1 } : { opacity: 0, y: 16, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={reduced ? { opacity: 1 } : { opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: reduced ? 0 : 0.22, ease: [0.2, 0.8, 0.2, 1] }}
          >
            <CheckCircle2 size={19} aria-hidden="true" />
            <span>{notice.message}</span>
            <button type="button" onClick={close} aria-label="Dismiss notification">
              <X size={17} aria-hidden="true" />
            </button>
            {!reduced && <span key={notice.id} className="toast-countdown" aria-hidden="true" />}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
