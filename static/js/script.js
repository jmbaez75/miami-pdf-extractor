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
        payload.map_file_folder = document.getElementById('map_file_folder')?.value;
        payload.sensitivity= document.getElementById('sensitivity')?.value || 5;
        payload.map_file=  document.getElementById('map_file')?.value;
        payload.excel_folder= document.getElementById('excel_folder')?.value;
        payload.mass_pdf_folder= document.getElementById('mass_pdf_folder')?.value
    }
    else if (activeTab.id=== 'tab2') {
        console.log('ejecutando tab2');
        payload.action="mapping",
        payload.pdf_folder= document.getElementById('pdf_folder')?.value;
        payload.pdf_input= payload.pdf_folder+ document.getElementById('pdf_input')?.value;
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
    .then(response => {
        // Intentamos leer el JSON siempre
        return response.json().then(data => {
            // Si el servidor respondió con 500 o 400, lanzamos el error
            if (!response.ok) {
                throw new Error(data.message || "Error desconocido del servidor");
            }
            return data;
        });
    })
    .then(data => {
        console.log("Respuesta del servidor:", data);

         if (data.status === 'started') {
            startProgressPolling(); // lectura On going
         } else {
            alert("Mensaje: " + data.message);// Galleta de éxito
        } 
    })
    .catch(error => {
        // AQUÍ ESTÁ TU GALLETA DE ERROR
        console.error("Error capturado:", error);
        alert("❌ ERROR: " + error.message); 
    });
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
    fetch('/fburo/update-config/', {


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


/**
 * Lógica dinámica para la Tab 4 - Editor de Plantilla
 * Asume que tienes un <tbody> con id="config-body" en tu HTML
 */

// 1. Cargar datos dinámicamente al entrar en la Tab 4
function loadTab3() {

    fetch('/fburo/get-template-data/')
    .then(r => {
        if (!r.ok) {
            return r.json().then(err => {
               
                alert(err.error || err.message || 'Error desconocido');
                throw new Error('handled');
            });
        }
        return r.json();
    })
    .then(data => {

        if (data.status === 'error') {
        alert(data.message);  // o un div de error en la UI
        return;    
        }

        const tbody = document.getElementById('config-body');
        tbody.innerHTML = "";
        data.forEach((row,index)=>{
            tbody.innerHTML += `
            <tr>
                <td>${row.original_text}</td>
                <td>
                    <input 
                    class="editable-header"
                    data-index="${index}"
                    value="${row.header_label}">
                </td>
            </tr>
            `;
        });
    });
}


function saveConfiguration() {
    let updates = [];
    // 1. Recolección de datos
    document.querySelectorAll('.editable-header').forEach(input => {
        updates.push({
            index: input.dataset.index,
            header_label: input.value // Esto captura lo que el usuario escribió
        });
    });

    // 2. Feedback visual (opcional pero recomendado)
    const btn = event.target;
    btn.disabled = true; // Evita clics dobles
    btn.innerText = "Guardando...";

    fetch('/fburo/save-template-config/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ updates: updates })
    })
    .then(r => r.json())
    .then(data => {
        console.log("Respuesta del servidor:", data);
        if(data.status === 'ok') {
            alert("Cambios guardados correctamente.");
        } else {
            alert("Error al guardar: " + (data.message || "Desconocido"));
        }
    })
    .catch(error => {
        console.error("Error en el fetch:", error);
        alert("Error de conexión con el servidor.");
    })
    .finally(() => {
        // Restaurar estado del botón
        btn.disabled = false;
        btn.innerText = "Guardar etiquetas";
    });
}

/******************  SISTEMA DE FILTROS ***************************/

// 1. Cargar datos del CSV al entrar en la tab
function loadTab4() {
    fetch('/fburo/get-filters/') // Asegúrate de tener esta URL en tus urls.py
    .then(r => r.json())
    .then(data => {
        const tbody = document.getElementById('body-filtros');
        tbody.innerHTML = "";
        data.forEach(row => {
            tbody.innerHTML += `
            <tr>
                <td><input type="text" name="original[]" value="${row.texto_original}" class="form-control"></td>
                <td><input type="text" name="reemplazo[]" value="${row.texto_reemplazo}" class="form-control"></td>
                <td><button type="button" class="btn btn-danger btn-sm" onclick="this.closest('tr').remove()">Eliminar</button></td>
            </tr>`;
        });
    });
}

// 2. Función para añadir fila manualmente
function agregarFilaFiltro() {
    const tbody = document.getElementById('body-filtros');
    tbody.insertAdjacentHTML('beforeend', `
        <tr>
            <td><input type="text" name="original[]" class="form-control"></td>
            <td><input type="text" name="reemplazo[]" class="form-control"></td>
            <td><button type="button" class="btn btn-danger btn-sm" onclick="this.closest('tr').remove()">Eliminar</button></td>
        </tr>`);
}

// 3. Guardar filtros
function saveFilters() {
    let originals = Array.from(document.querySelectorAll('input[name="original[]"]')).map(i => i.value);
    let reemplazos = Array.from(document.querySelectorAll('input[name="reemplazo[]"]')).map(i => i.value);

    fetch('/fburo/save-filters/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ original: originals, reemplazo: reemplazos })
    })
    .then(r => r.json())
    .then(data => {
        alert(data.message || "Guardado correctamente");
    });
}

let progressInterval = null;

function startProgressPolling() {
    const container = document.getElementById('progress-container');
    const bar = document.getElementById('batch-progress-bar');
    const text = document.getElementById('batch-progress-text');
    const btn = document.querySelector('#tab1 button[onclick*="batch"]');

    container.style.display = 'block';
    bar.value = 0;
    text.innerText = "Iniciando...";
    btn.disabled = true;

    if (progressInterval) clearInterval(progressInterval);

    progressInterval = setInterval(() => {
        fetch('/fburo/batch-progress/')
            .then(r => r.json())
            .then(job => {
                const total = job.total || 0;
                const current = job.current || 0;
                const pct = total > 0 ? Math.round((current / total) * 100) : 0;

                bar.value = pct;
                text.innerText = total > 0 ? `${current}/${total} (${pct}%)` : "Preparando...";

                if (job.status === 'done') {
                    clearInterval(progressInterval);
                    text.innerText = "Completado ✅";
                    btn.disabled = false;
                    alert("Lote procesado. Excel en " + job.result);
                } else if (job.status === 'error') {
                    clearInterval(progressInterval);
                    text.innerText = "Error ❌";
                    btn.disabled = false;
                    alert("❌ ERROR: " + job.message);
                }
            })
            .catch(err => {
                clearInterval(progressInterval);
                btn.disabled = false;
                console.error("Error consultando progreso:", err);
            });
    }, 1000);
}