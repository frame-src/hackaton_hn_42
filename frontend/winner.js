async function loadWinner() {
    const winnerContainer = document.getElementById('winner-card');
    const projectsContainer = document.getElementById('projects-container');
    
    winnerContainer.innerHTML = "<p>Loading winner...</p>";
    projectsContainer.innerHTML = "<p>Loading projects...</p>";
  
    try {
      // --- MOCK DATA ---
      const winner = {
        id: 1,
        name: "Ehi Oleg",
        description: "Visionary software engineer blending performance, minimalism, and green tech innovation. He codes wood solid nukeproof C--",
        quote: "If I win 1$ for each Hackaton I won, I would have 0$, Felicita' e' un bicchiere di vino con un panino.",
        image: "img/month_winner.jpg"
      };
  
      const projects = [
        {
          name: "Minishell",
          url: "https://projects.intra.42.fr/projects/42cursus-minishell/projects_users/4399105",
          image: "img/minishell.png"
        },
        {
          name: "Fract-ol",
          url: "https://projects.intra.42.fr/projects/42cursus-fract-ol/projects_users/4302678",
          image: "img/fract-ol.png"
        },
        {
          name: "Philosophers",
          url: "https://projects.intra.42.fr/projects/42cursus-philosophers/projects_users/4399097",
          image: "img/philosophers.png"
        }
      ];
  
      // --- RENDER WINNER ---
      winnerContainer.innerHTML = `
        <img src="${winner.image}" alt="${winner.name}" id="month_winner">
        <h2>${winner.name}</h2>
        <p class="description">${winner.description}</p>
        <p class="quote">${winner.quote}</class>
      `;
  
      // --- RENDER PROJECTS ---
      projectsContainer.innerHTML = projects.map(p => `
        <div class="project-card">
          <a href="${p.url}" target="_blank">
            <img src="${p.image}" alt="${p.name}">
            <h3>${p.name}</h3>
          </a>
        </div>
      `).join('');
  
      // --- Real fetch version for later ---
      // const winnerRes = await fetch('/api/winner');
      // const winner = await winnerRes.json();
      // const projectsRes = await fetch(`/api/winner/${winner.id}/projects`);
      // const projects = await projectsRes.json();
  
    } catch (err) {
      console.error(err);
      winnerContainer.innerHTML = "<p>Error loading winner data.</p>";
      projectsContainer.innerHTML = "<p>Error loading projects.</p>";
    }
  }
  
  window.onload = loadWinner;
  