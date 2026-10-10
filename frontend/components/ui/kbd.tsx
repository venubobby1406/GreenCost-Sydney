import { cn } from '@/lib/utils';

/** Keyboard shortcut hint. */
export default function Kbd({ children, className }: { children: React.ReactNode; className?: string }) {
  return <kbd className={cn('ui-kbd', className)}>{children}</kbd>;
}
