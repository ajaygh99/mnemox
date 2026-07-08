// login.js — Mnemox Auth UI
// Handles sign in / sign up via Supabase auth (proxied through service worker)

'use strict';

var signinForm = document.getElementById('signin-form');
var signupForm = document.getElementById('signup-form');
var errorMsg   = document.getElementById('error-msg');

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.style.display = 'block';
}
function hideError() {
  errorMsg.style.display = 'none';
}

// Toggle between sign in / sign up
document.getElementById('goto-signup').addEventListener('click', function() {
  signinForm.style.display = 'none';
  signupForm.style.display = 'block';
  hideError();
});
document.getElementById('goto-signin').addEventListener('click', function() {
  signupForm.style.display = 'none';
  signinForm.style.display = 'block';
  hideError();
});

// ── Sign In ──────────────────────────────────────────────────────────────────
document.getElementById('signin-btn').addEventListener('click', function() {
  var email    = document.getElementById('signin-email').value.trim();
  var password = document.getElementById('signin-password').value;
  if (!email || !password) return showError('Please enter email and password.');

  var btn = document.getElementById('signin-btn');
  btn.textContent = 'Signing in…';
  btn.disabled = true;
  hideError();

  chrome.runtime.sendMessage(
    { type: 'MNEMOX_AUTH_SIGNIN', payload: { email: email, password: password } },
    function(response) {
      btn.textContent = 'Sign In';
      btn.disabled = false;
      if (response && response.success) {
        // Close login page, open main popup
        window.location.href = 'popup.html';
      } else {
        showError((response && response.error) || 'Sign in failed. Check credentials.');
      }
    }
  );
});

// ── Sign Up ──────────────────────────────────────────────────────────────────
document.getElementById('signup-btn').addEventListener('click', function() {
  var email    = document.getElementById('signup-email').value.trim();
  var password = document.getElementById('signup-password').value;
  if (!email || !password) return showError('Please fill all fields.');
  if (password.length < 8) return showError('Password must be at least 8 characters.');

  var btn = document.getElementById('signup-btn');
  btn.textContent = 'Creating account…';
  btn.disabled = true;
  hideError();

  chrome.runtime.sendMessage(
    { type: 'MNEMOX_AUTH_SIGNUP', payload: { email: email, password: password } },
    function(response) {
      btn.textContent = 'Create Free Account';
      btn.disabled = false;
      if (response && response.success) {
        // Show confirmation or redirect
        if (response.needsConfirmation) {
          signinForm.style.display = 'none';
          signupForm.style.display = 'none';
          hideError();
          showConfirmationScreen(email);
        } else {
          window.location.href = 'popup.html';
        }
      } else {
        showError((response && response.error) || 'Sign up failed. Try again.');
      }
    }
  );
});

// -- Post-signup confirmation screen -----------------------------------------
// Built with real DOM nodes (not innerHTML +=) so it can't accidentally wipe
// out existing listeners, and so the user's email is inserted safely.
function showConfirmationScreen(email) {
  var wrap = document.createElement('div');
  wrap.id = 'confirm-screen';
  wrap.style.cssText = 'width:100%;text-align:center;padding:12px 2px 4px;';

  var icon = document.createElement('div');
  icon.style.cssText = 'font-size:40px;margin-bottom:12px;';
  icon.textContent = '📬';

  var title = document.createElement('div');
  title.style.cssText = 'color:#a78bfa;font-weight:700;font-size:16px;margin-bottom:8px;';
  title.textContent = 'Account created — check your email!';

  var body = document.createElement('div');
  body.style.cssText = 'color:#9ca3af;font-size:13px;line-height:1.5;margin-bottom:18px;';
  var strong = document.createElement('strong');
  strong.style.color = '#e5e7eb';
  strong.textContent = email;
  body.appendChild(document.createTextNode('We sent a confirmation link to '));
  body.appendChild(strong);
  body.appendChild(document.createTextNode('. Click the link in that email, then come back here and sign in.'));

  var backBtn = document.createElement('button');
  backBtn.className = 'btn btn-secondary';
  backBtn.textContent = 'Back to Sign In';
  backBtn.addEventListener('click', function() {
    wrap.remove();
    signupForm.style.display = 'none';
    signinForm.style.display = 'block';
  });

  wrap.appendChild(icon);
  wrap.appendChild(title);
  wrap.appendChild(body);
  wrap.appendChild(backBtn);
  document.body.appendChild(wrap);
}
