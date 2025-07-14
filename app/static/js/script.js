// Alternar visualização de senha
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');

if (togglePassword && passwordInput) { // Verifica se os elementos existem
  togglePassword.addEventListener('click', () => {
    const type = passwordInput.type === 'password' ? 'text' : 'password';
    passwordInput.type = type;
    togglePassword.classList.toggle('fa-eye');
    togglePassword.classList.toggle('fa-eye-slash');
  });
}

// Login via API
const loginBtn = document.getElementById('loginBtn');
const usernameInput = document.getElementById('username'); // Corrigido de 'email' para 'username'
const errorMsg = document.getElementById('errorMsg');

if (loginBtn) { // Verifica se o botão existe
  loginBtn.addEventListener('click', async (event) => {
    event.preventDefault(); // Impede o envio padrão do formulário

    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
      errorMsg.textContent = 'Por favor, preencha todos os campos.';
      return;
    }

    try {
      // Cria o objeto FormData para enviar username e password como form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token); // Armazena o refresh token
        errorMsg.textContent = 'Login bem-sucedido!';
        // Redireciona para a página principal/dashboard
        window.location.href = '/static/main.html'; // Próxima tela
      } else {
        const errorData = await response.json();
        errorMsg.textContent = errorData.detail || 'Erro ao fazer login. Credenciais inválidas.';
      }
    } catch (error) {
      console.error('Erro de rede ou API:', error);
      errorMsg.textContent = 'Erro de conexão. Tente novamente mais tarde.';
    }
  });
}