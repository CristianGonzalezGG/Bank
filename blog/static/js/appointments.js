document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Validación de formulario mejorada
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Animación de entrada para elementos de la tabla
    const tableRows = document.querySelectorAll('.appointment-table tbody tr');
    tableRows.forEach((row, index) => {
        row.style.animation = `slideIn 0.3s ease-out ${index * 0.1}s forwards`;
    });

    // Datepicker personalizado
    const datePicker = document.querySelector('input[type="date"]');
    if (datePicker) {
        flatpickr(datePicker, {
            minDate: "today",
            dateFormat: "Y-m-d",
            locale: "es",
            showMonths: 2,
            animate: true
        });
    }

    // TimePicker personalizado
    const timePicker = document.querySelector('input[type="time"]');
    if (timePicker) {
        flatpickr(timePicker, {
            enableTime: true,
            noCalendar: true,
            dateFormat: "H:i",
            minTime: "09:00",
            maxTime: "18:00",
            locale: "es"
        });
    }

    // Función para confirmar cancelación
    window.confirmCancel = function(appointmentId) {
        Swal.fire({
            title: '¿Está seguro?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#4e73df',
            cancelButtonColor: '#e74a3b',
            confirmButtonText: 'Sí, cancelar cita',
            cancelButtonText: 'No, mantener cita'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = `/appointments/${appointmentId}/cancel/`;
            }
        });
    };

    // Notificaciones Toast
    const showToast = (message, type = 'success') => {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} show`;
        toast.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">${type === 'success' ? 'Éxito' : 'Error'}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    };

    // Manejar mensajes de Django
    const messages = document.querySelectorAll('.django-message');
    messages.forEach(message => {
        showToast(message.textContent, message.dataset.type);
        message.remove();
    });
}); 