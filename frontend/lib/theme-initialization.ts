export const THEME_KEY = 'greencost-theme';

/** Static, non-identifying preference bootstrap executed before first paint. */
export const themeInitialization = `(function(){var t;try{t=localStorage.getItem('${THEME_KEY}')}catch(e){}if(t!=='dark'&&t!=='light')t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.dataset.theme=t;document.documentElement.style.colorScheme=t})()`;
