'use client';

import {Moon, Sun} from 'lucide-react';
import {setTheme, useTheme} from '@/lib/theme';

export default function ThemeToggle() {
 const theme = useTheme();
 const label = `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`;
 return <button type="button" className="theme-toggle" aria-label={label} title={label} onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
  <Moon className="theme-icon-moon" size={19} aria-hidden="true"/>
  <Sun className="theme-icon-sun" size={19} aria-hidden="true"/>
 </button>;
}
