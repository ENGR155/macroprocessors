/* Framework-free enhancements; navigation and reading do not require JavaScript. */
(() => {
  'use strict';
  // Preserve the native button semantics on Quarto's mobile navigation toggle.
  document.querySelector('.navbar-toggler')?.removeAttribute('role');
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
