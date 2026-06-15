// Actualización del slider y guardado automático (opcional)
document.getElementById('sensitivity')?.addEventListener('input', function(e) {
    const val = e.target.value;
    document.getElementById('val-sensitivity').innerText = val;
    
    // Opcional: guardar el valor cada vez que se mueve
    saveToBackend('sensitivity', val);
});

// Función de ejecución mejorada para incluir el valor actual
function executeAction(type) {
    // 1. Aquí capturas lo que hay en pantalla
    const payload = {
        type: type,
        sensitivity: document.getElementById('sensitivity')?.value || 5,
        pdf_path: document.getElementById('pdf_input')?.value,
        output_path: document.getElementById('map_out')?.value
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
    .then(data => alert("Respuesta del servidor: " + data.status));
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