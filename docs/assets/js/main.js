/**
 * ConvertMD Main JavaScript
 * Handles navigation interactions, UI showcase switching, terminal copying, and 3-state theme management.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Theme Management (Light / Dark / System)
  const themeToggleBtns = document.querySelectorAll('.theme-toggle-btn');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)');

  function getStoredTheme() {
    return localStorage.getItem('convertmd-theme') || 'system';
  }

  function applyTheme(theme) {
    let effectiveTheme = theme;
    if (theme === 'system') {
      effectiveTheme = systemPrefersDark.matches ? 'dark' : 'light';
    }

    document.documentElement.setAttribute('data-theme', effectiveTheme);

    // Update active state on the 3 buttons
    themeToggleBtns.forEach(btn => {
      const btnTheme = btn.getAttribute('data-theme-set');
      if (btnTheme === theme) {
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
      }
    });

    // Notify 3D canvas if background changes
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: effectiveTheme } }));
  }

  // Initial theme application
  const initialTheme = getStoredTheme();
  applyTheme(initialTheme);

  // Listen for clicks on theme buttons
  themeToggleBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const selectedTheme = e.currentTarget.getAttribute('data-theme-set');
      localStorage.setItem('convertmd-theme', selectedTheme);
      applyTheme(selectedTheme);
    });
  });

  // Listen for system theme changes when in 'system' mode
  systemPrefersDark.addEventListener('change', () => {
    if (getStoredTheme() === 'system') {
      applyTheme('system');
    }
  });

  // 2. UI Showcase Tab Switcher
  const showcaseTabs = document.querySelectorAll('.showcase-tab-btn');
  const showcaseImg = document.getElementById('showcase-main-img');

  const SHOWCASE_IMAGES = {
    '1': './assets/images/app-preview-1.svg',
    '2': './assets/images/app-preview-2.svg',
    '3': './assets/images/app-preview-3.svg'
  };

  showcaseTabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      const stateId = e.currentTarget.getAttribute('data-preview');
      showcaseTabs.forEach(t => t.classList.remove('active'));
      e.currentTarget.classList.add('active');

      if (showcaseImg && SHOWCASE_IMAGES[stateId]) {
        showcaseImg.style.opacity = '0.3';
        setTimeout(() => {
          showcaseImg.src = SHOWCASE_IMAGES[stateId];
          showcaseImg.style.opacity = '1';
        }, 150);
      }
    });
  });

  // 3. Terminal Commands Copy
  const copyTerminalBtn = document.getElementById('btn-copy-terminal');
  if (copyTerminalBtn) {
    copyTerminalBtn.addEventListener('click', async () => {
      const commands = `git clone https://github.com/davidcaroo/convertMD.git\ncd convertMD\npip install -r requirements.txt\npython main.py`;
      try {
        await navigator.clipboard.writeText(commands);
        const originalText = copyTerminalBtn.innerHTML;
        copyTerminalBtn.innerHTML = `<span>Comandos Copiados</span>`;
        copyTerminalBtn.classList.add('btn-emerald');

        setTimeout(() => {
          copyTerminalBtn.innerHTML = originalText;
          copyTerminalBtn.classList.remove('btn-emerald');
        }, 2000);
      } catch (err) {
        console.error('Error al copiar comandos:', err);
      }
    });
  }

  // 4. Navbar scroll blur enhancement
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.style.borderBottomColor = 'rgba(137, 180, 250, 0.2)';
      navbar.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.5)';
    } else {
      navbar.style.borderBottomColor = 'var(--border-subtle)';
      navbar.style.boxShadow = 'none';
    }
  });

  // 5. Set current year in footer
  const yearElem = document.getElementById('footer-year');
  if (yearElem) {
    yearElem.textContent = new Date().getFullYear();
  }
});
