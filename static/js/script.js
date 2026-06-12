// Gestión de pestañas
function openTab(evt, tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(tabName).style.display = 'block';
    evt.currentTarget.classList.add('active');
}

// Lógica de ejecución
function executeAction(type) {
    // Aquí iría tu lógica de conexión con Django/Python
    console.log("Ejecutando proceso: " + type);
    alert("Iniciando proceso: " + type);
}

function saveToBackend(key, value) {
    fetch('/fburo/update-config/', { // Ajusta la URL según tu config
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 'key': key, 'value': value })
    });
}