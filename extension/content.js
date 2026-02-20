// content.js - Se inyecta en todas las páginas

let apiUrl = 'https://api.buloradar.com'; // Cambiar en producción

// Detectar contenido sospechoso
function detectarContenidoSospechoso() {
    const textos = document.querySelectorAll('p, h1, h2, h3, article, .tweet-text, .css-901oao');
    
    textos.forEach(elemento => {
        const texto = elemento.innerText;
        
        // Enviar a background para análisis
        chrome.runtime.sendMessage({
            type: 'ANALIZAR_TEXTO',
            texto: texto,
            url: window.location.href
        });
    });
    
    // Detectar imágenes
    const imagenes = document.querySelectorAll('img');
    imagenes.forEach(img => {
        if (img.src && img.src.startsWith('http')) {
            chrome.runtime.sendMessage({
                type: 'ANALIZAR_IMAGEN',
                url: img.src,
                pagina: window.location.href
            });
        }
    });
}

// Añadir overlay de advertencia
function mostrarAlerta(buloData) {
    const alerta = document.createElement('div');
    alerta.className = 'buloradar-alerta';
    alerta.innerHTML = `
        <div class="buloradar-alerta-header">
            <img src="${chrome.runtime.getURL('icons/icon48.png')}" alt="BuloRadar">
            <h3>⚠️ ¡ALERTA DE POSIBLE BULO!</h3>
            <button class="buloradar-cerrar">&times;</button>
        </div>
        <div class="buloradar-alerta-content">
            <p><strong>${buloData.titulo}</strong></p>
            <p>${buloData.descripcion}</p>
            <div class="buloradar-verdad">
                <h4>🔍 REALIDAD:</h4>
                <p>${buloData.verdad}</p>
            </div>
            ${buloData.fuentes ? `
                <div class="buloradar-fuentes">
                    <h4>Fuentes:</h4>
                    <ul>
                        ${buloData.fuentes.map(f => `<li><a href="${f.url}" target="_blank">${f.nombre}</a></li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
        <div class="buloradar-alerta-footer">
            <button class="buloradar-btn buloradar-ver-mas">Ver detalle completo</button>
            <button class="buloradar-btn buloradar-reportar">Reportar error</button>
        </div>
    `;
    
    // Estilos
    const styles = `
        .buloradar-alerta {
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 400px;
            background: #1a1a1a;
            color: white;
            border: 3px solid #ffde00;
            border-radius: 8px;
            padding: 15px;
            z-index: 999999;
            font-family: 'Space Grotesk', sans-serif;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            animation: buloradar-slideIn 0.3s ease;
        }
        
        @keyframes buloradar-slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .buloradar-alerta-header {
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        
        .buloradar-alerta-header img {
            width: 24px;
            height: 24px;
        }
        
        .buloradar-alerta-header h3 {
            margin: 0;
            flex: 1;
            color: #ffde00;
        }
        
        .buloradar-cerrar {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
        }
        
        .buloradar-verdad {
            background: rgba(0,255,136,0.1);
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #00ff88;
            margin: 10px 0;
        }
        
        .buloradar-verdad h4 {
            color: #00ff88;
            margin: 0 0 5px 0;
        }
        
        .buloradar-fuentes ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        
        .buloradar-fuentes a {
            color: #ffde00;
            text-decoration: none;
        }
        
        .buloradar-alerta-footer {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .buloradar-btn {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .buloradar-ver-mas {
            background: #ffde00;
            color: #1a1a1a;
        }
        
        .buloradar-reportar {
            background: transparent;
            color: white;
            border: 1px solid #ffde00;
        }
        
        .buloradar-btn:hover {
            transform: translateY(-2px);
        }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
    
    document.body.appendChild(alerta);
    
    // Cerrar alerta
    alerta.querySelector('.buloradar-cerrar').onclick = () => alerta.remove();
    
    // Ver más
    alerta.querySelector('.buloradar-ver-mas').onclick = () => {
        chrome.runtime.sendMessage({
            type: 'ABRIR_DETALLE',
            buloId: buloData.id
        });
    };
}

// Escuchar respuestas del background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'MOSTRAR_ALERTA') {
        mostrarAlerta(message.data);
    }
});

// Iniciar detección cuando la página cargue
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', detectarContenidoSospechoso);
} else {
    detectarContenidoSospechoso();
}

// Observar cambios en el DOM (para páginas dinámicas como Twitter)
const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
        if (mutation.addedNodes.length) {
            detectarContenidoSospechoso();
        }
    }
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
