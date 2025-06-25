// 👉 URL base da sua API Django
const baseUrl = "http://127.0.0.1:8000/api";
let accessToken = null;

// ---------------------------------------------
// 🔑 LOGIN
// ---------------------------------------------
document.getElementById('login-btn').addEventListener('click', async () => {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  const response = await fetch(`${baseUrl}/token/`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email, password }) // <-- corrigido aqui
  });

  if (response.ok) {
    const data = await response.json();
    accessToken = data.access;
    document.getElementById('token-status').innerText = "✅ Login OK!";
    console.log("Token JWT:", accessToken);
  } else {
    document.getElementById('token-status').innerText = "❌ Login falhou!";
  }
});

// ---------------------------------------------
// 📚 LISTAR LIVROS
// ---------------------------------------------
document.getElementById('listar-livros-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const response = await fetch(`${baseUrl}/livros/`, {
    headers: { "Authorization": `Bearer ${accessToken}` }
  });

  const data = await response.json();
  document.getElementById('livros-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// ➕ CRIAR LIVRO (Admin)
// ---------------------------------------------
document.getElementById('criar-livro-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const titulo = document.getElementById('livro-titulo').value;
  const autor = document.getElementById('livro-autor').value;
  const genero = document.getElementById('livro-genero').value;
  const descricao = document.getElementById('livro-descricao').value;

  const response = await fetch(`${baseUrl}/livros/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${accessToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ titulo, autor, genero, descricao })
  });

  const data = await response.json();
  document.getElementById('livros-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// ✏️ EDITAR LIVRO (Admin)
// ---------------------------------------------
document.getElementById('editar-livro-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const id = document.getElementById('livro-id-editar').value;
  const titulo = document.getElementById('livro-titulo').value;
  const autor = document.getElementById('livro-autor').value;
  const genero = document.getElementById('livro-genero').value;
  const descricao = document.getElementById('livro-descricao').value;

  const response = await fetch(`${baseUrl}/livros/${id}/`, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${accessToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ titulo, autor, genero, descricao })
  });

  const data = await response.json();
  document.getElementById('livros-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// ❌ DESATIVAR LIVRO (Admin)
// ---------------------------------------------
document.getElementById('desativar-livro-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const id = document.getElementById('livro-id-editar').value;
  const response = await fetch(`${baseUrl}/livros/${id}/`, {
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${accessToken}`
    }
  });

  if (response.status === 204) {
    document.getElementById('livros-result').innerText = "✅ Livro desativado com sucesso!";
  } else {
    const data = await response.json();
    document.getElementById('livros-result').innerText = JSON.stringify(data, null, 2);
  }
});

// ---------------------------------------------
// 📝 CRIAR RESERVA
// ---------------------------------------------
document.getElementById('criar-reserva-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const livroId = document.getElementById('livro-id-reserva').value;

  const response = await fetch(`${baseUrl}/reservas/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${accessToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ livro: livroId })
  });

  const data = await response.json();
  document.getElementById('reserva-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// 📋 LISTAR MINHAS RESERVAS
// ---------------------------------------------
document.getElementById('listar-reservas-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const response = await fetch(`${baseUrl}/reservas/`, {
    headers: { "Authorization": `Bearer ${accessToken}` }
  });

  const data = await response.json();
  document.getElementById('reserva-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// ✅ CONFIRMAR RESERVA
// ---------------------------------------------
document.getElementById('confirmar-reserva-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const reservaId = document.getElementById('reserva-id-confirmar').value;

  const response = await fetch(`${baseUrl}/reservas/${reservaId}/confirmar/`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${accessToken}` }
  });

  const data = await response.json();
  document.getElementById('reserva-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// 🔙 DEVOLVER EMPRÉSTIMO
// ---------------------------------------------
async function devolverEmprestimo(emprestimoId) {
  if (!accessToken) return alert("Faça login primeiro!");

  const response = await fetch(`${baseUrl}/emprestimos/${emprestimoId}/devolver/`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${accessToken}` }
  });

  const data = await response.json();
  alert(JSON.stringify(data, null, 2));
}
// Exemplo de uso:
// devolverEmprestimo(123); // Substitua 123 pelo ID real

// ---------------------------------------------
// 📊 DASHBOARD
// ---------------------------------------------
document.getElementById('dashboard-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const response = await fetch(`${baseUrl}/dashboard/`, {
    headers: { "Authorization": `Bearer ${accessToken}` }
  });

  const data = await response.json();
  document.getElementById('dashboard-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// 📧 LEMBRETE DEVOLUÇÃO
// ---------------------------------------------
document.getElementById('lembrete-devolucao-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const response = await fetch(`${baseUrl}/lembrete-devolucao/`, {
    headers: { "Authorization": `Bearer ${accessToken}` }
  });

  const data = await response.json();
  document.getElementById('notificacoes-result').innerText = JSON.stringify(data, null, 2);
});

// ---------------------------------------------
// 📧 AVISAR RESERVAS EXPIRANDO
// ---------------------------------------------
document.getElementById('avisar-expirando-btn').addEventListener('click', async () => {
  if (!accessToken) return alert("Faça login primeiro!");

  const response = await fetch(`${baseUrl}/avisar-reservas-expirando/`, {
    headers: { "Authorization": `Bearer ${accessToken}` }
  });

  const data = await response.json();
  document.getElementById('notificacoes-result').innerText = JSON.stringify(data, null, 2);
});
