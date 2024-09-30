document.getElementById('filterButton').addEventListener('click', function() {
    // Obtener los valores de los filtros
    var accountNumber = document.getElementById('account_number').value.toLowerCase();
    var status = document.getElementById('status').value;
    var createdFrom = document.getElementById('created_from').value;
    var createdTo = document.getElementById('created_to').value;

    // Obtener la lista de clientes
    var clients = document.querySelectorAll('#clientList .client-card');

    clients.forEach(function(client) {
        // Obtener los atributos de datos del cliente
        var clientAccountNumber = client.getAttribute('data-account-number').toLowerCase();
        var clientStatus = client.getAttribute('data-status');
        var clientCreatedAt = client.getAttribute('data-created-at');

        // Filtrar por número de cuenta
        var showClient = true;
        
        if (accountNumber && !clientAccountNumber.includes(accountNumber)) {
            showClient = false;
        }

        // Filtrar por estado de cuenta
        if (status && clientStatus !== status) {
            showClient = false;
        }

        // Filtrar por fecha de creación
        if (createdFrom && clientCreatedAt < createdFrom) {
            showClient = false;
        }

        if (createdTo && clientCreatedAt > createdTo) {
            showClient = false;
        }

        // Mostrar u ocultar el cliente dependiendo del filtro
        if (showClient) {
            client.style.display = "block";
        } else {
            client.style.display = "none";
        }
    });
});
