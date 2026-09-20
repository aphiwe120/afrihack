document.addEventListener('DOMContentLoaded', () => {
  const switcher = document.createElement('button');
  const currentPath = window.location.pathname;
  const isAdvisorView = currentPath.includes('advisor-dashboard');
  const isClientView = currentPath.includes('dashboard') && !isAdvisorView;

  switcher.type = 'button';
  switcher.innerText = isAdvisorView ? 'Switch to Client' : 'Switch to Advisor';
  switcher.style.position = 'fixed';
  switcher.style.bottom = '20px';
  switcher.style.right = '20px';
  switcher.style.zIndex = '9999';
  switcher.style.padding = '8px 16px';
  switcher.style.backgroundColor = '#1E293B';
  switcher.style.color = 'white';
  switcher.style.borderRadius = '9999px';
  switcher.style.fontSize = '12px';
  switcher.style.opacity = '0.3';
  switcher.style.transition = 'opacity 0.2s';
  switcher.style.cursor = 'pointer';
  switcher.style.border = 'none';
  switcher.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';

  switcher.addEventListener('mouseover', () => {
    switcher.style.opacity = '1';
  });

  switcher.addEventListener('mouseout', () => {
    switcher.style.opacity = '0.3';
  });

  switcher.addEventListener('click', () => {
    if (isAdvisorView) {
      switcher.innerText = 'Switch to Client';
      window.location.href = 'dashboard.html';
    } else if (isClientView) {
      switcher.innerText = 'Switch to Advisor';
      window.location.href = 'advisor-dashboard.html';
    }
  });

  document.body.append(switcher);
});
