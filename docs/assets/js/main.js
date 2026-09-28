/**
 * ConvertMD Main JavaScript
 * Handles navigation interactions, UI showcase switching, terminal copying, and scroll effects.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. UI Showcase Tab Switcher
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

  // 2. Terminal Commands Copy
  const copyTerminalBtn = document.getElementById('btn-copy-terminal');
  if (copyTerminalBtn) {
    copyTerminalBtn.addEventListener('click', async () => {
      const commands = `git clone https://github.com/davidcaroo/convertMD.git\ncd convertMD\npip install -r requirements.txt\npython main.py`;
      try {
        await navigator.clipboard.writeText(commands);
        const originalText = copyTerminalBtn.innerHTML;
        copyTerminalBtn.innerHTML = `<span>✓ ¡Comandos Copiados!</span>`;
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

  // 3. Navbar scroll blur enhancement
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.style.borderBottomColor = 'rgba(137, 180, 250, 0.2)';
      navbar.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.6)';
    } else {
      navbar.style.borderBottomColor = 'var(--border-subtle)';
      navbar.style.boxShadow = 'none';
    }
  });

  // 4. Set current year in footer
  const yearElem = document.getElementById('footer-year');
  if (yearElem) {
    yearElem.textContent = new Date().getFullYear();
  }
});
