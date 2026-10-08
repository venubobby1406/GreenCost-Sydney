'use client';

import {useSyncExternalStore} from 'react';
import {THEME_KEY} from './theme-initialization';

export type Theme = 'light' | 'dark';
const THEME_EVENT = 'greencost-theme-change';

function snapshot(): Theme {
 return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
}

function applyTheme(theme: Theme) {
 document.documentElement.dataset.theme = theme;
 document.documentElement.style.colorScheme = theme;
 window.dispatchEvent(new Event(THEME_EVENT));
}

export function setTheme(theme: Theme) {
 try { localStorage.setItem(THEME_KEY, theme); } catch { /* Still usable when storage is unavailable. */ }
 applyTheme(theme);
}

function subscribe(onChange: () => void) {
 const media = window.matchMedia('(prefers-color-scheme: dark)');
 const syncPreference = () => {
  let saved: string | null = null;
  try { saved = localStorage.getItem(THEME_KEY); } catch { /* Follow the system preference. */ }
  applyTheme(saved === 'dark' || saved === 'light' ? saved : media.matches ? 'dark' : 'light');
 };
 const storageChange = (event: StorageEvent) => {
  if (event.key === THEME_KEY || event.key === null) syncPreference();
 };
 window.addEventListener(THEME_EVENT, onChange);
 window.addEventListener('storage', storageChange);
 media.addEventListener('change', syncPreference);
 return () => {
  window.removeEventListener(THEME_EVENT, onChange);
  window.removeEventListener('storage', storageChange);
  media.removeEventListener('change', syncPreference);
 };
}

export function useTheme(): Theme {
 return useSyncExternalStore(subscribe, snapshot, () => 'light');
}

export const chartPalette = {
 light: {sustainable:'#00753e', conventional:'#b85b25', grid:'#deded7', text:'#62695f', surface:'#fffefa', foreground:'#222820', components:['#00753e','#d28249','#7f9f6a','#b2b879','#5c8f94','#aa8b62','#7e827b','#b47f87']},
 dark: {sustainable:'#98c56e', conventional:'#e5a16c', grid:'#30382e', text:'#a5ada1', surface:'#151815', foreground:'#f7f7f2', components:['#98c56e','#e5a16c','#72996b','#ced68d','#78b2b8','#baa17b','#a0a59b','#d69ca5']},
};

export const compactMoney = (value: number) => new Intl.NumberFormat('en-AU', {style:'currency', currency:'AUD', notation:'compact', maximumFractionDigits:1}).format(value);
