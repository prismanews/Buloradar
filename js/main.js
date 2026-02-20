// main.js - Funcionalidad principal de BuloRadar

// Datos de ejemplo para la base de datos de bulos
const bulosData = [
    {
        id: 1,
        title: "¿Nuevo virus creado en laboratorio?",
        description: "Afirma que el último brote viral fue creado artificialmente",
        truth: "Estudios internacionales confirman origen natural. La OMS desmiente esta teoría.",
        platform: "twitter",
        category: "salud",
        dangerLevel: "alto",
        date: "2024-01-15",
        source: "https://twitter.com/...",
        image: null
    },
    {
        id: 2,
        title: "Manipulación de cifras de empleo",
        description: "Afirma que las estadísticas de paro están falseadas",
        truth: "Los datos del INE son verificables y auditados por organismos independientes",
        platform: "tiktok",
        category: "politica",
        dangerLevel: "medio",
        date: "2024-01-14",
        source: "https://tiktok.com/...",
        image: null
    },
    {
        id: 3,
        title: "Nueva moneda digital obligatoria",
        description: "Asegura que el gobierno implantará una moneda digital para controlar ahorros",
        truth: "No hay ningún proyecto de ley en curso. El Banco Central lo desmiente",
        platform: "instagram",
        category: "economia",
        dangerLevel: "bajo",
        date: "2024-01-13",
        source: "https://instagram.com/...",
        image: null
    },
    {
        id: 4,
        title: "Vacunas contienen microchips",
        description: "Teoría conspirativa sobre seguimiento a través de vacunas",
        truth: "Estudios científicos demuestran composición. Organismos de salud lo desmienten",
        platform: "facebook",
        category: "salud",
        dangerLevel: "alto",
        date: "2024-01-12",
        source: "https://facebook.com/...",
        image: null
    },
    {
        id: 5,
        title: "Manipulación electoral en elecciones",
        description: "Afirma que hubo fraude masivo en votos por correo",
        truth: "Auditoría independiente confirma transparencia del proceso",
        platform: "twitter",
        category: "politica",
        dangerLevel: "alto",
        date: "2024-01-11",
        source: "https://twitter.com/...",
        image: null
    },
    {
        id: 6,
        title: "Nueva cura milagrosa para el cáncer",
        description: "Promueve tratamiento alternativo sin base científica",
        truth: "Asociaciones médicas advierten sobre peligros de tratamientos no probados",
        platform: "telegram",
        category: "salud",
        dangerLevel: "alto",
        date: "2024-01-10",
        source: "https://t.me/...",
        image: null
    }
];

// Contador animado
function animateCounter() {
    const counter = document.querySelector('.counter');
    const target = parseInt(counter.getAttribute('data-target'));
    let current = 0;
    const increment = target / 100;
    
    const updateCounter = setInterval(() => {
        current += increment;
        if (current >= target) {
            counter.textContent = target;
            clearInterval(updateCounter);
        } else {
            counter.textContent = Math.floor(current);
        }
    }, 20);
}

// Cargar bulos en el feed
function loadBulosFeed(bulos = bulosData) {
    const feedContainer = document.getElementById('buloFeed');
    if (!feedContainer) return;
    
    feedContainer.innerHTML = '';
    
    bulos.forEach(bulo => {
        const card = createBuloCard(bulo);
        feedContainer.appendChild(card);
    });
}

// Crear tarjeta de bulo
function createBuloCard(bulo) {
    const card = document.createElement('div');
    card.className = 'bulo-card';
    
    const dangerClass = bulo.dangerLevel === 'alto' ? 'alto' : 
                       bulo.dangerLevel === 'medio' ? 'medio' : 'bajo';
    
    const platformIcons = {
        twitter: 'fa-brands fa-x-twitter',
        tiktok: 'fa-brands fa-tiktok',
        instagram: 'fa-brands fa-instagram',
        facebook: 'fa-brands fa-facebook',
        telegram: 'fa-brands fa-telegram'
    };
    
    const platformIcon = platformIcons[bulo.platform] || 'fa-solid fa-globe';
    
    card.innerHTML = `
        <div class="bulo-header">
            <div class="bulo-platform ${bulo.platform}">
                <i class="${platformIcon}"></i>
                <span>${bulo.platform.charAt(0).toUpperCase() + bulo.platform.slice(1)}</span>
            </div>
            <span class="bulo-danger ${dangerClass}">${bulo.dangerLevel.toUpperCase()}</span>
        </div>
        <div class="bulo-content">
            <h3 class="bulo-title">${bulo.title}</h3>
            <p class="bulo-description">${bulo.description}</p>
            <div class="bulo-truth">
                <h4>🔍 REALIDAD:</h4>
                <p>${bulo.truth}</p>
            </div>
        </div>
        <div class="bulo-footer">
            <span class="bulo-date">${formatDate(bulo.date)}</span>
            <button class="btn-share" onclick="shareBulo(${bulo.id})">
                <i class="fa-solid fa-share"></i>
            </button>
        </div>
    `;
    
    return card;
}

// Formatear fecha
function formatDate(dateString) {
    const options = { day: 'numeric', month: 'short', year: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-ES', options);
}

// Compartir bulo
function shareBulo(id) {
    const bulo = bulosData.find(b => b.id === id);
    if (bulo && navigator.share) {
        navigator.share({
            title: bulo.title,
            text: `${bulo.description} - REALIDAD: ${bulo.truth}`,
            url: window.location.href
        });
    } else {
        alert('¡Comparte la verdad! Copia el enlace manualmente.');
    }
}

// Cargar base de datos
function loadDatabase(bulos = bulosData) {
    const databaseGrid = document.getElementById('databaseGrid');
    if (!databaseGrid) return;
    
    databaseGrid.innerHTML = '';
    
    bulos.forEach(bulo => {
        const item = createDatabaseItem(bulo);
        databaseGrid.appendChild(item);
    });
}

// Crear item de base de datos
function createDatabaseItem(bulo) {
    const item = document.createElement('div');
    item.className = 'database-item';
    
    const dangerClass = bulo.dangerLevel === 'alto' ? 'alto' : 
                       bulo.dangerLevel === 'medio' ? 'medio' : 'bajo';
    
    item.innerHTML = `
        <div class="database-item-header">
            <span class="database-category">${bulo.category}</span>
            <span class="database-danger ${dangerClass}">${bulo.dangerLevel}</span>
        </div>
        <h4 class="database-title">${bulo.title}</h4>
        <p class="database-description">${bulo.description}</p>
        <div class="database-footer">
            <span class="database-date">${formatDate(bulo.date)}</span>
            <button class="btn-view" onclick="viewBuloDetails(${bulo.id})">Ver detalles</button>
        </div>
    `;
    
    return item;
}

// Ver detalles del bulo
function viewBuloDetails(id) {
    const bulo = bulosData.find(b => b.id === id);
    if (bulo) {
        alert(`BULO: ${bulo.title}\n\nREALIDAD: ${bulo.truth}\n\nFuente: ${bulo.source}`);
    }
}

// Filtrar bulos
function filterBulos() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const category = document.getElementById('categoryFilter')?.value || '';
    const dateFilter = document.getElementById('dateFilter')?.value || '';
    const dangerFilter = document.getElementById('dangerFilter')?.value || '';
    
    const filtered = bulosData.filter(bulo => {
        // Filtro de búsqueda
        const matchesSearch = bulo.title.toLowerCase().includes(searchTerm) ||
                            bulo.description.toLowerCase().includes(searchTerm) ||
                            bulo.truth.toLowerCase().includes(searchTerm);
        
        // Filtro de categoría
        const matchesCategory = !category || bulo.category === category;
        
        // Filtro de nivel de peligro
        const matchesDanger = !dangerFilter || bulo.dangerLevel === dangerFilter;
        
        // Filtro de fecha (simplificado)
        let matchesDate = true;
        if (dateFilter) {
            const buloDate = new Date(bulo.date);
            const now = new Date
