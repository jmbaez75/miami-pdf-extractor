// Actualización del slider y guardado automático (opcional)
document.getElementById('sensitivity')?.addEventListener('input', function(e) {
    const val = e.target.value;
    document.getElementById('val-sensitivity').innerText = val;
    
    // Opcional: guardar el valor cada vez que se mueve
    saveToBackend('sensitivity', val);
});

// Función de ejecución mejorada para incluir el valor actual
function executeAction(type) {

    // Se sabe las pestaña asctiva todo el rato
    const activeTab = document.querySelector('.tab-content:not([style*="display: none"])');
    let payload = { type: type };
    // 1. Aquí capturas lo que hay en pantalla
    
    if (activeTab.id === 'tab1') {
        payload.action = "screening",
        payload.sensitivity= document.getElementById('sensitivity')?.value || 5;
        payload.excel_out= document.getElementById('excel_out')?.value;
        payload.mass_pdf_folder= document.getElementById('mass_pdf_folder')?.value
    }
    else if (activeTab.id=== 'tab2') {
        payload.action="mapping",
        payload.pdf_input= document.getElementById('pdf_input')?.value;
        payload.map_out= document.getElementById('map_out').value

    };
    console.log(payload);
    // 2. Aquí envías el payload (la caja con toda la información)
    fetch('/fburo/execute-path/', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload) // <--- ¡AQUÍ ESTÁ EL CAMBIO!
    })
    .then(response => response.json())
    .then(data => console.log("Respuesta del servidor: " + data.status));
}

// Helper para obtener el token CSRF (esencial en Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para guardar cambios en tiempo real
function updateConfig(key, value) {
    fetch('/update-config/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 'key': key, 'value': value })
    })
    .then(response => response.json())
    .then(data => console.log("Guardado:", data));
}

function openTab(evt, tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName).style.display = 'block';
    evt.currentTarget.classList.add('active');
}