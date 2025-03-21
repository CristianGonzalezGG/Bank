// Asegúrate de que este archivo esté incluido en tu template
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture');
    const clientId = document.getElementById('client_id').value; // Asegúrate de tener este campo oculto en tu template
    
    // Acceder a la webcam
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            console.error('Error al acceder a la webcam:', err);
        });

    captureButton.addEventListener('click', function() {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convertir a base64
        const imageData = canvas.toDataURL('image/jpeg');
        
        // Enviar al servidor
        fetch('/capture_image/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                imageData: imageData,
                clientId: clientId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar la imagen en la página
                const previewImage = document.getElementById('preview');
                if (previewImage) {
                    previewImage.src = data.image_url;
                    previewImage.style.display = 'block';
                }
            } else {
                console.error('Error:', data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});

// Función para obtener el token CSRF
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