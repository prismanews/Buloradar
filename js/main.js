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
            const now = new Date();
            const diffDays = Math.floor((now - buloDate) / (1000 * 60 * 60 * 24));
            
            if (dateFilter === '24h' && diffDays > 1) matchesDate = false;
            else if (dateFilter === 'week' && diffDays > 7) matchesDate = false;
            else if (dateFilter === 'month' && diffDays > 30) matchesDate = false;
            else if (dateFilter === 'year' && diffDays > 365) matchesDate = false;
        }
        
        return matchesSearch && matchesCategory && matchesDanger && matchesDate;
    });
    
    loadDatabase(filtered);
}

// Modal functionality
function initModal() {
    const modal = document.getElementById('reportModal');
    const reportBtn = document.querySelector('.btn-report');
    const closeBtn = document.querySelector('.close-modal');
    const reportForm = document.getElementById('reportForm');
    
    if (reportBtn) {
        reportBtn.onclick = () => {
            modal.style.display = 'block';
        };
    }
    
    if (closeBtn) {
        closeBtn.onclick = () => {
            modal.style.display = 'none';
        };
    }
    
    window.onclick = (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    };
    
    if (reportForm) {
        reportForm.onsubmit = (e) => {
            e.preventDefault();
            alert('¡Gracias por tu reporte! Nuestro equipo lo revisará.');
            modal.style.display = 'none';
            reportForm.reset();
        };
    }
}

// Filter buttons functionality
function initFilterButtons() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Here you would filter the feed based on category
            const category = btn.textContent.toLowerCase();
            if (category === 'todos') {
                loadBulosFeed(bulosData);
            } else {
                const filtered = bulosData.filter(b => b.category === category);
                loadBulosFeed(filtered);
            }
        });
    });
}

// Smooth scroll for navigation
function initSmoothScroll() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// Active nav link on scroll
function initActiveNav() {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    animateCounter();
    loadBulosFeed();
    loadDatabase();
    initModal();
    initFilterButtons();
    initSmoothScroll();
    initActiveNav();
    
    // Add event listeners for search and filters
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const dateFilter = document.getElementById('dateFilter');
    const dangerFilter = document.getElementById('dangerFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterBulos);
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterBulos);
    }
    
    if (dateFilter) {
        dateFilter.addEventListener('change', filterBulos);
    }
    
    if (dangerFilter) {
        dangerFilter.addEventListener('change', filterBulos);
    }
    
    // Hero CTA buttons
    const primaryBtn = document.querySelector('.btn-primary');
    if (primaryBtn) {
        primaryBtn.addEventListener('click', () => {
            document.getElementById('feed').scrollIntoView({ behavior: 'smooth' });
        });
    }
    
    const secondaryBtn = document.querySelector('.btn-secondary');
    if (secondaryBtn) {
        secondaryBtn.addEventListener('click', () => {
            alert('BuloRadar rastrea automáticamente miles de fuentes para detectar y desmentir bulos en tiempo real. ¡Tu colaboración es clave!');
        });
    }
});

// Add some CSS for database items (to be added to styles.css)
const style = document.createElement('style');
style.textContent = `
    .database-item {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .database-item:hover {
        border-color: var(--primary);
        transform: translateY(-3px);
    }
    
    .database-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .database-category {
        background: var(--primary);
        color: var(--dark);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .database-danger {
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .database-title {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: var(--light);
    }
    
    .database-description {
        color: #999;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    .database-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
    }
    
    .database-date {
        color: #666;
        font-size: 0.8rem;
    }
    
    .btn-view {
        background: var(--primary);
        color: var(--dark);
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .btn-view:hover {
        background: var(--secondary);
        color: var(--light);
    }
`;

document.head.appendChild(style);
