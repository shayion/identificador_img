// app/static/js/register.js
document.addEventListener('DOMContentLoaded', () => {
    const registerBtn = document.getElementById('registerBtn');
    const fullNameInput = document.getElementById('full_name');
    const usernameInput = document.getElementById('username'); // Campo para o username
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const successMsg = document.getElementById('successMsg');
    const errorMsg = document.getElementById('errorMsg'); // Para erros da API

    if (registerBtn) {
        registerBtn.addEventListener('click', async (event) => {
            event.preventDefault(); // Impede o envio padrão do formulário

            successMsg.style.display = "none";
            errorMsg.textContent = ""; // Limpa erros anteriores

            const full_name = fullNameInput.value.trim();
            const username = usernameInput.value.trim(); // Pega o valor do username
            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();
            const confirmPassword = confirmPasswordInput.value.trim();

            if (!full_name || !username || !email || !password || !confirmPassword) {
                errorMsg.textContent = "Por favor, preencha todos os campos.";
                return;
            }

            if (password !== confirmPassword) {
                errorMsg.textContent = "As senhas não coincidem.";
                return;
            }

            try {
                const response = await fetch('/api/v1/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json', // Enviamos JSON para o registro
                    },
                    body: JSON.stringify({
                        full_name: full_name,
                        username: username,
                        email: email,
                        password: password
                    }),
                });

                if (response.ok) {
                    // const data = await response.json(); // Se a API retornar dados do usuário
                    successMsg.style.display = "block";
                    // Limpar campos
                    fullNameInput.value = "";
                    usernameInput.value = "";
                    emailInput.value = "";
                    passwordInput.value = "";
                    confirmPasswordInput.value = "";
                    // Opcional: Redirecionar após alguns segundos
                    setTimeout(() => {
                        window.location.href = '/static/index.html'; // Redireciona para o login
                    }, 2000); // 2 segundos
                } else {
                    const errorData = await response.json();
                    errorMsg.textContent = errorData.detail || "Erro no cadastro. Tente novamente.";
                }
            } catch (error) {
                console.error('Erro de rede ou API:', error);
                errorMsg.textContent = 'Erro de conexão. Tente novamente mais tarde.';
            }
        });
    }
});