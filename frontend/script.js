async function callBackend(endpoint) {
    try {
        const res = await fetch(endpoint);
        const data = await res.json();
        document.getElementById('output').textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById('output').textContent = 'Error fetching data';
        console.error(err);
    }
}

async function loadHallOfFame() {
    const container = document.getElementById('hall-of-fame');
    container.innerHTML = "<p>Loading...</p>";
  
    try {
    //   const res = await fetch('/api/hall-of-fame'); // replace with your actual backend endpoint
    //   const data = await res.json();
      const data = [
        {
          "name": "Tomek Rosinski",
          "description": "The first Polish computer programmer. National Hero as Lewandowski. Wrote the first algorithm intended for a Polish Coal machine.",
          "quotes": "'I have it, so it's your problem'",
          "image": "https://cdn.intra.42.fr/users/a8740924b5824fcbdb689f71e96735dc/trosinsk.jpg"
        },
        {
          "name": "Francesco",
          "description": "Invented the first compiler and coined the term 'debugging'.",
          "image": "https://upload.wikimedia.org/wikipedia/commons/3/37/Grace_Hopper_and_UNIVAC.jpg"
        },
        {
          "name": "Linus Torvalds",
          "description": "Creator of the Linux kernel — the backbone of modern computing.",
          "image": "https://upload.wikimedia.org/wikipedia/commons/6/69/Linus_Torvalds.jpeg"
        },
        {
          "name": "Dennis Ritchie",
          "description": "Created the C programming language and co-developed Unix.",
          "image": "https://upload.wikimedia.org/wikipedia/commons/2/23/Dennis_Ritchie_2011.jpg"
        }
    ]  
      if (!Array.isArray(data)) {
        container.innerHTML = "<p>Invalid response format.</p>";
        return;
      }
  
      container.innerHTML = ''; // Clear loading text
      
      data.forEach(person => {
        const card = document.createElement('div');
        card.className = 'person-card';
  
        card.innerHTML = `
          <img src="${person.image || 'placeholder.png'}" alt="${person.name}">
          <h3>${person.name}</h3>
          <p>${person.description || ''}</p>
          <p>${person.quotes || ''}</p>
        `;
  
        container.appendChild(card);
      });
    } catch (err) {
      console.error(err);
      container.innerHTML = "<p>Error loading Hall of Fame.</p>";
    }
}
  
window.onload = loadHallOfFame;
  