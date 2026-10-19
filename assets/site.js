/* Framework-free enhancements; navigation and reading do not require JavaScript. */
(() => {
  'use strict';
  // Preserve the native button semantics on Quarto's mobile navigation toggle.
  document.querySelector('.navbar-toggler')?.removeAttribute('role');
  for (const group of document.querySelectorAll('[data-tabs]')) {
    const tabs = [...group.querySelectorAll('[role="tab"]')];
    const activate = (next, focus = false) => {
      for (const tab of tabs) {
        const selected = tab === next;
        tab.setAttribute('aria-selected', String(selected));
        tab.tabIndex = selected ? 0 : -1;
        document.getElementById(tab.getAttribute('aria-controls')).hidden = !selected;
      }
      if (focus) next.focus();
    };
    for (const [index, tab] of tabs.entries()) {
      tab.addEventListener('click', () => activate(tab));
      tab.addEventListener('keydown', event => {
        let target;
        if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft') target = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') target = 0;
        if (event.key === 'End') target = tabs.length - 1;
        if (target !== undefined) { event.preventDefault(); activate(tabs[target], true); }
      });
    }
  }
  for (const table of document.querySelectorAll('main table')) {
    if (table.parentElement.classList.contains('table-responsive')) continue;
    const wrapper = document.createElement('div');
    wrapper.className = 'table-responsive';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    const heading = table.closest('section')?.querySelector('h2,h3');
    wrapper.setAttribute('aria-label', (heading?.textContent.trim() || 'Project data') + ' table');
    table.before(wrapper);
    wrapper.append(table);
  }
})();
