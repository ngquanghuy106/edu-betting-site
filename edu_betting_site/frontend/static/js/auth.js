const usernameInput = document.getElementById("username");

if (usernameInput) {
	const rules = {
		length: username => username.length >= 5 && username.length <= 50,
		characters: username => /^[a-zA-Z0-9_]+$/.test(username),
		reserved: username => {
			const reserved = ["owner", "admin", "moderator"];
			return !reserved.some(word => username.toLowerCase().includes(word));
		}
	};

	usernameInput.addEventListener("input", () => {
		const username = usernameInput.value;

		for (const [rule, validate] of Object.entries(rules)) {
			const element = document.querySelector(
				`[data-username-rule="${rule}"]`
			);

			const indicator = element.querySelector("span");
			const met = validate(username);

			element.classList.toggle("met", met);
			indicator.textContent = met ? "✓" : "✕";
		}
	});

	usernameInput.dispatchEvent(new Event("input"));
}

const passwordInput = document.getElementById("password");

if (passwordInput) {
	const rules = {
		length: password => password.length >= 8 && password.length <= 128,
		lowercase: password => /[a-z]/.test(password),
		uppercase: password => /[A-Z]/.test(password),
		number: password => /\d/.test(password),
		special: password => /[^a-zA-Z0-9\s]/.test(password)
	};

	passwordInput.addEventListener("input", () => {
		const password = passwordInput.value;

		for (const [rule, validate] of Object.entries(rules)) {
			const element = document.querySelector(`[data-rule="${rule}"]`);
			const indicator = element.querySelector("span");
			const met = validate(password);

			element.classList.toggle("met", met);
			indicator.textContent = met ? "✓" : "✕";
		}
	});
}
