document.addEventListener('DOMContentLoaded', () => {
  const registerForm = document.getElementById('registerForm');
  const responseMessage = document.getElementById('responseMessage');
})

// register user
registerForm.addEventListener('submit', async(e) => {

  e.preventDefault();

  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;

  const response = await fetch('/register', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          name,
          email
      })
  })

  const data = await response.json();
  responseMessage.textContent = data.message;

})
