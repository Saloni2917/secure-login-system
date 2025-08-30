// ============================
// Helpers
// ============================
function $(sel, root = document) { return root.querySelector(sel); }
function $all(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

function setError(input, msg) {
  if (!input) return;
  const field = input.closest('.field');
  const msgEl = field ? field.querySelector('.error-msg') : null;
  if (msgEl) msgEl.textContent = msg;
  input.setCustomValidity(msg || '');
  if (msg) input.reportValidity();
}

function clearError(input) { setError(input, ''); }

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function passwordChecks(v) {
  return {
    length: v.length >= 8,
    upper: /[A-Z]/.test(v),
    lower: /[a-z]/.test(v),
    digit: /\d/.test(v),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(v),
  };
}

document.addEventListener('DOMContentLoaded', () => {
  // Show/Hide password
  $all('.toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const sel = btn.getAttribute('data-toggle');
      const input = $(sel);
      if (!input) return;
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });

  // Caps Lock detection
  function watchCaps(inputSel, indicatorSel) {
    const input = $(inputSel);
    const ind = $(indicatorSel);
    if (!input || !ind) return;
    const update = (e) => {
      const on = e.getModifierState && e.getModifierState('CapsLock');
      ind.textContent = on ? 'On' : 'Off';
      ind.classList.toggle('caps--on', on);
      ind.classList.toggle('caps--off', !on);
    };
    input.addEventListener('keyup', update);
    input.addEventListener('keydown', update);
  }
  watchCaps('#login-password', '#caps-login');
  watchCaps('#reg-password', '#caps-reg');

  // Password strength meter
  (function () {
    const input = $('#reg-password');
    const bar = $('#pw-meter-bar');
    if (!input || !bar) return;
    const rules = {
      length: $('#rule-length'),
      upper: $('#rule-upper'),
      lower: $('#rule-lower'),
      digit: $('#rule-digit'),
      special: $('#rule-special'),
    };
    input.addEventListener('input', () => {
      const v = input.value || '';
      const checks = passwordChecks(v);
      Object.entries(checks).forEach(([k, ok]) => {
        if (rules[k]) rules[k].classList.toggle('valid', ok);
      });
      const score = Object.values(checks).reduce((a, ok) => a + (ok ? 1 : 0), 0);
      bar.style.width = (score / 5) * 100 + '%';
      clearError(input);
    });
  })();

  // Admin Users filter
  (function () {
    const search = $('#userSearch');
    const table = $('#usersTable');
    if (!search || !table) return;
    const rows = () => table.querySelectorAll('tbody tr');
    search.addEventListener('input', () => {
      const q = search.value.toLowerCase();
      rows().forEach(tr => {
        const text = tr.innerText.toLowerCase();
        tr.style.display = text.includes(q) ? '' : 'none';
      });
    });
  })();

   // Clear captcha input on page load
  (function () {
    const captchaInput = document.querySelector("input[name='captcha']");
    if (captchaInput) captchaInput.value = "";
  })();

  // Universal form validation
  $all('form').forEach(form => {
    form.addEventListener('input', (e) => {
      const t = e.target;
      if (t.matches('input, select, textarea')) clearError(t);
    });

    form.addEventListener('submit', (e) => {
      let firstInvalid = null;
      let ok = true;

      const username = form.querySelector("input[name='username']");
      const email = form.querySelector("input[name='email']");
      const passLogin = form.querySelector("#login-password");
      const passReg = form.querySelector("#reg-password");
      const captcha = form.querySelector("input[name='captcha']");
      const captchaAns = form.querySelector("input[name='captcha_answer']");

      // CAPTCHA validation FIRST (stop submit early if wrong)
      if (captcha && captchaAns) {
        const user = (captcha.value || '').trim();
        const truth = (captchaAns.value || '').trim();
        if (!user) {
          e.preventDefault();
          setError(captcha, 'Please answer the CAPTCHA.');
          captcha.focus();
          return;
        } else if (user !== truth) {
          e.preventDefault();
          setError(captcha, 'Incorrect CAPTCHA answer.');
          captcha.focus();
          return;
        } else {
          clearError(captcha);
        }
      }

      // Username
      if (username) {
        const v = (username.value || '').trim();
        if (!v) {
          ok = false; firstInvalid ||= username;
          setError(username, 'Please enter a username.');
        } else if (v.length < 3) {
          ok = false; firstInvalid ||= username;
          setError(username, 'Username must be at least 3 characters.');
        } else clearError(username);
      }

      // Email
      if (email) {
        const v = (email.value || '').trim();
        if (!v) {
          ok = false; firstInvalid ||= email;
          setError(email, 'Please enter your email address.');
        } else if (!EMAIL_RE.test(v)) {
          ok = false; firstInvalid ||= email;
          setError(email, 'Enter a valid email address (e.g., you@example.com).');
        } else clearError(email);
      }

      // Password (login)
      if (passLogin) {
        const v = passLogin.value || '';
        if (!v) {
          ok = false; firstInvalid ||= passLogin;
          setError(passLogin, 'Please enter your password.');
        } else if (v.length < 6) {
          ok = false; firstInvalid ||= passLogin;
          setError(passLogin, 'Password must be at least 6 characters.');
        } else clearError(passLogin);
      }

      // Password (register)
      if (passReg) {
        const v = passReg.value || '';
        const checks = passwordChecks(v);
        const strong = Object.values(checks).every(Boolean);
        if (!strong) {
          ok = false; firstInvalid ||= passReg;
          setError(passReg, 'Password must be at least 8 chars with UPPER, lower, number, special.');
        } else clearError(passReg);
      }
      
      
      const role = form.querySelector("select[name='role']"); 

      if (role) {
        const v = (role.value || '').trim();
      if (!v) {
        ok = false; firstInvalid ||= role;
        setError(role, 'Please select a role.');
    } else if (v === 'Admin') {
        ok = false; firstInvalid ||= role;
        setError(role, 'Admin role is restricted. Please choose User.');
    } else {
        clearError(role);
  }
}
 
      if (!ok) {
        e.preventDefault();
        if (firstInvalid) {
          firstInvalid.focus({ preventScroll: false });
          firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  });
});
