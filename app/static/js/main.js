// main.js

document.addEventListener("DOMContentLoaded", () => {
  const loginBtn = document.getElementById("loginBtn");
  const errorMsg = document.getElementById("errorMsg");

  if (loginBtn) {
    loginBtn.addEventListener("click", async () => {
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value.trim();

      if (!email || !password) {
        errorMsg.textContent = "Por favor, preencha todos os campos.";
        return;
      }

      try {
        const response = await fetch("http://localhost:3000/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
          localStorage.setItem("userEmail", email);
          window.location.href = "dashboard.html";
        } else {
          errorMsg.textContent = data.message || "Credenciais inválidas.";
        }
      } catch (error) {
        errorMsg.textContent = "Erro ao conectar com o servidor.";
      }
    });
  }

  // DASHBOARD - exibir email do usuário e logout
  const userEmail = localStorage.getItem("userEmail");
  const userEmailSpan = document.getElementById("userEmail");
  const logoutBtn = document.getElementById("logoutBtn");

  if (userEmailSpan) {
    if (!userEmail) {
      window.location.href = "index.html";
    } else {
      userEmailSpan.textContent = userEmail;
    }
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.removeItem("userEmail");
      window.location.href = "index.html";
    });
  }
});
