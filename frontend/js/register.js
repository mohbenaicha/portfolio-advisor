import { BASE_URL, reCAPTCHA_SITE_KEY } from "./config.js";
import { validateRecaptcha, showElement, hideElement } from "./utils.js";

const loadingScreen = document.getElementById("loading-screen");

document.getElementById("register-btn").addEventListener("click", () => {
    const registerBox = document.getElementById("register-box");
    registerBox.classList.toggle("hidden");
});

document.querySelector("#register-box span").addEventListener("click", () => {
    const registerBox = document.getElementById("register-box");
    registerBox.classList.add("hidden");
});

document.getElementById("register-submit-btn").addEventListener("click", async () => {
    showElement(loadingScreen, "Processing your registration request...");
    const recaptchaToken = await grecaptcha.execute(reCAPTCHA_SITE_KEY);
    const isRecaptchaValid = await validateRecaptcha(recaptchaToken);
    if (!isRecaptchaValid) return;
    
    const emailInput = document.getElementById("email-input").value.trim();

    // Basic email validation
    const validateEmail = (email) => {
        try {
            const emailValidator = new URL(`mailto:${email}`);
            return emailValidator.protocol === "mailto:";
        } catch {
            return false;
        }
    };

    if (!validateEmail(emailInput)) {
        alert("Invalid email address. Please enter a valid email.");
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/request-key`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email: emailInput }),
        });

        if (response.ok) {
            const data = await response.json();
            alert(data.message + " Please check your inbox shortly.");
        } else {
            const errorData = await response.json();
            console.error("Error response:", errorData);

            // Handle array or object content
            let errorDetails = "";
            if (Array.isArray(errorData.detail)) {
                errorDetails = errorData.detail
                    .map((item) => {
                        if (item.ctx && item.ctx.reason) {
                            return item.ctx.reason; // Extract specific reason
                        }
                        return JSON.stringify(item); // Fallback for other structures
                    })
                    .join(", ");
            } else {
                errorDetails = JSON.stringify(errorData.detail, null, 2);
            }

            alert("Error. Please make sure your email address matches username@domain.ext | error: \n" + errorDetails);
        }
    } catch (error) {
        console.error("Network error:", error);
        alert("An unexpected error occurred. Please try again later.");
    } finally {
        hideElement(loadingScreen);
    }
});