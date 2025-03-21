function toggleChatbot() {
    const chatbot = document.getElementById('chatbot');
    chatbot.style.display = chatbot.style.display === 'block' ? 'none' : 'block';
}

function botResponse(question) {
    let response = '';

    switch (question) {
        case '¿Dónde puedo registrar un nuevo cliente?':
            response = 'Para registrar un nuevo cliente, diríjase a la sección de "Clientes" en el menú principal.';
            break;
        case '¿Cómo puedo ver la información de la tarjeta de un cliente?':
            response = 'Puede ver la información de la tarjeta de un cliente en la sección "Información de cuentas" dentro del menú principal.<a href="/get-card-info">Click Aqui</a>';
            break;
        case '¿Qué trámites puedo realizar en línea?':
            response = 'Puede realizar trámites como solicitud de créditos, consultas de movimientos, y actualización de datos personales. ';
            break;
        default:
            response = 'Lo siento, no tengo una respuesta para esa pregunta.';
            break;
    }

    document.getElementById('chatbot-response').innerHTML = `<p><strong>Respuesta:</strong> ${response}</p>`;
}
