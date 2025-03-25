class SecurityQuestionsManager {
    constructor() {
        this.questions = new Set();
        this.initializeEventListeners();
        this.setupStrengthMeters();
    }

    initializeEventListeners() {
        document.querySelectorAll('.security-question').forEach(select => {
            select.addEventListener('change', (e) => this.handleQuestionChange(e));
        });

        document.querySelectorAll('.security-answer').forEach(input => {
            input.addEventListener('input', (e) => this.checkAnswerStrength(e));
        });
    }

    handleQuestionChange(event) {
        const selectedValue = event.target.value;
        const previousValue = event.target.dataset.previousValue;

        if (previousValue) {
            this.questions.delete(previousValue);
        }

        if (this.questions.has(selectedValue)) {
            event.target.value = previousValue || '';
            Swal.fire({
                title: 'Pregunta Duplicada',
                text: 'Por favor seleccione una pregunta diferente',
                icon: 'warning',
                confirmButtonText: 'Entendido'
            });
            return;
        }

        this.questions.add(selectedValue);
        event.target.dataset.previousValue = selectedValue;
        this.updateOtherQuestions(selectedValue);
    }

    updateOtherQuestions(selectedValue) {
        document.querySelectorAll('.security-question').forEach(select => {
            if (select.value !== selectedValue) {
                Array.from(select.options).forEach(option => {
                    option.disabled = this.questions.has(option.value) && option.value !== select.value;
                });
            }
        });
    }

    checkAnswerStrength(event) {
        const answer = event.target.value;
        const meter = event.target.nextElementSibling;
        const strength = this.calculateAnswerStrength(answer);

        meter.innerHTML = `
            <div class="strength-${strength.level}" 
                 style="width: ${strength.percentage}%"></div>
        `;

        meter.setAttribute('data-strength', strength.level);
    }

    calculateAnswerStrength(answer) {
        let score = 0;
        
        if (answer.length >= 8) score += 1;
        if (/[A-Z]/.test(answer)) score += 1;
        if (/[0-9]/.test(answer)) score += 1;
        if (/[^A-Za-z0-9]/.test(answer)) score += 1;

        const strengthLevels = {
            0: { level: 'weak', percentage: 33 },
            1: { level: 'weak', percentage: 33 },
            2: { level: 'medium', percentage: 66 },
            3: { level: 'strong', percentage: 100 },
            4: { level: 'strong', percentage: 100 }
        };

        return strengthLevels[score];
    }

    setupStrengthMeters() {
        document.querySelectorAll('.security-answer').forEach(input => {
            const meter = document.createElement('div');
            meter.className = 'answer-strength-meter';
            input.parentNode.insertBefore(meter, input.nextSibling);
        });
    }
}

class ImageUploadManager {
    constructor() {
        this.setupDropZone();
        this.setupImagePreview();
    }

    setupDropZone() {
        const dropZone = document.getElementById('uploadBox');
        const fileInput = document.getElementById('id_imageSave');

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('highlight');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('highlight');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            fileInput.files = dt.files;
            this.handleFiles(dt.files);
        });
    }

    setupImagePreview() {
        const fileInput = document.getElementById('id_imageSave');
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }

    handleFiles(files) {
        if (files.length === 0) return;

        const file = files[0];
        if (!file.type.startsWith('image/')) {
            Swal.fire({
                title: 'Error',
                text: 'Por favor seleccione un archivo de imagen válido',
                icon: 'error'
            });
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('imagePreview').src = e.target.result;
            document.getElementById('fileName').textContent = file.name;
        };
        reader.readAsDataURL(file);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', () => {
    const securityManager = new SecurityQuestionsManager();
    const imageManager = new ImageUploadManager();

    // Validación del formulario
    const form = document.getElementById('clientForm');
    form.addEventListener('submit', (e) => {
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
            
            Swal.fire({
                title: 'Error de Validación',
                text: 'Por favor complete todos los campos requeridos correctamente',
                icon: 'error'
            });
        }
        form.classList.add('was-validated');
    });
}); 