
document.addEventListener("DOMContentLoaded", function () {

    // Show / Hide password
    document.querySelectorAll("[data-toggle-password]").forEach(button => {

        button.addEventListener("click", function () {

            const inputId = button.dataset.togglePassword;
            const input = document.getElementById(inputId);

            if (!input) return;

            const showPassword = input.type === "password";

            input.type = showPassword ? "text" : "password";

            button.textContent = showPassword ? "Hide" : "Show";

            button.setAttribute(
                "aria-label",
                showPassword ? "Hide password" : "Show password"
            );
        });
    });


    // Signup password confirmation
    const signupForm = document.getElementById("signupForm");

    if (signupForm) {

        const password = document.getElementById("signupPassword");
        const confirmPassword = document.getElementById("confirmPassword");
        const error = document.getElementById("passwordError");

        signupForm.addEventListener("submit", function (event) {

            error.textContent = "";

            if (password.value !== confirmPassword.value) {

                event.preventDefault();

                error.textContent = "Passwords do not match.";

                confirmPassword.focus();

                return;
            }

            if (password.value.length < 8) {

                event.preventDefault();

                error.textContent =
                    "Password must contain at least 8 characters.";

                password.focus();
            }
        });

        confirmPassword.addEventListener("input", function () {
            error.textContent = "";
        });
    }

});
