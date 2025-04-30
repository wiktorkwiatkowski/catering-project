fetch('/menu')
  .then(response => response.json())
  .then(data => {
    const list = document.getElementById('menu-list');
    data.forEach(item => {
      const li = document.createElement('li');
      li.textContent = `${item.name} — ${item.price} zł`;
      list.appendChild(li);
    });
  });
