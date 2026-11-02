document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const loginBtn = form.querySelector("button");
  const usernameInput = form.querySelector("input[name='username']");
  const passwordInput = form.querySelector("input[name='password']");
  const rememberCheckbox = form.querySelector("input[type='checkbox']");

  /* ===============================
     REMEMBER ME (localStorage)
  =============================== */
  if (localStorage.getItem("rememberedUser")) {
    usernameInput.value = localStorage.getItem("rememberedUser");
    rememberCheckbox.checked = true;
  }

  /* ===============================
     FORM SUBMIT HANDLER
  =============================== */
  form.addEventListener("submit", (e) => {
    // basic validation
    if (!usernameInput.value || !passwordInput.value) {
      e.preventDefault();
      alert("Please fill in all fields");
      return;
    }

    // remember user
    if (rememberCheckbox.checked) {
      localStorage.setItem("rememberedUser", usernameInput.value);
    } else {
      localStorage.removeItem("rememberedUser");
    }

    // loading state
    loginBtn.disabled = true;
    loginBtn.innerText = "Signing in...";
    loginBtn.style.opacity = "0.8";
  });

  /* ===============================
     OPTIONAL: ENTER KEY UX POLISH
  =============================== */
  [usernameInput, passwordInput].forEach(input => {
    input.addEventListener("focus", () => {
      input.parentElement?.classList.add("active");
    });
    input.addEventListener("blur", () => {
      input.parentElement?.classList.remove("active");
    });
  });
});
