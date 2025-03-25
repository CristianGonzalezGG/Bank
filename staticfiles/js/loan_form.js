document.addEventListener('DOMContentLoaded', function() {
    const searchStep = document.getElementById('searchStep');
    const verificationStep = document.getElementById('verificationStep');
    const loanFormStep = document.getElementById('loanFormStep');
    const clientSearch = document.getElementById('clientSearch');
    const searchResults = document.getElementById('searchResults');
    let selectedClientId = null;

    // Client Search
    let searchTimeout;
    clientSearch.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = e.target.value;
            if (query.length >= 3) {
                fetchClients(query);
            } else {
                searchResults.innerHTML = '';
                searchResults.classList.add('d-none');
            }
        }, 300);
    });

    async function fetchClients(query) {
        try {
            const response = await fetch(`/api/search-clients/?q=${query}`);
            const data = await response.json();
            
            searchResults.innerHTML = '';
            searchResults.classList.remove('d-none');
            
            data.forEach(client => {
                const item = document.createElement('div');
                item.className = 'list-group-item search-result-item';
                item.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">${client.name}</h6>
                            <small class="text-muted">Doc: ${client.cardId}</small>
                        </div>
                        <button class="btn btn-sm btn-outline-primary select-client-btn">
                            Seleccionar
                        </button>
                    </div>
                `;
                
                item.querySelector('.select-client-btn').addEventListener('click', () => {
                    selectClient(client);
                });
                
                searchResults.appendChild(item);
            });
        } catch (error) {
            console.error('Error fetching clients:', error);
        }
    }

    function selectClient(client) {
        // Check for active loans
        checkActiveLoan(client.id).then(hasActiveLoan => {
            if (hasActiveLoan) {
                showActiveLoanModal(client);
            } else {
                selectedClientId = client.id;
                proceedToVerification(client);
            }
        });
    }

    async function checkActiveLoan(clientId) {
        try {
            const response = await fetch(`/api/check-active-loan/${clientId}/`);
            const data = await response.json();
            return data.hasActiveLoan;
        } catch (error) {
            console.error('Error checking active loan:', error);
            return false;
        }
    }

    function showActiveLoanModal(client) {
        const modal = new bootstrap.Modal(document.getElementById('activeLoanModal'));
        const detailsList = document.getElementById('activeLoanDetails');
        
        // Populate active loan details
        fetch(`/api/active-loan-details/${client.id}/`)
            .then(response => response.json())
            .then(loan => {
                detailsList.innerHTML = `
                    <li>Monto: $${loan.amount}</li>
                    <li>Fecha inicio: ${loan.start_date}</li>
                    <li>Saldo pendiente: $${loan.remaining_balance}</li>
                `;
                modal.show();
            });
    }

    function proceedToVerification(client) {
        // Send verification code
        fetch('/api/send-verification-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ clientId: client.id })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI to show verification step
                searchStep.classList.add('d-none');
                verificationStep.classList.remove('d-none');
                updateStepperProgress(2);
            }
        });
    }

    // Code verification input handling
    const codeInputs = document.querySelectorAll('.code-input');
    codeInputs.forEach((input, index) => {
        input.addEventListener('keyup', (e) => {
            if (e.key >= 0 && e.key <= 9) {
                if (index < codeInputs.length - 1) {
                    codeInputs[index + 1].focus();
                }
            } else if (e.key === 'Backspace') {
                if (index > 0) {
                    codeInputs[index - 1].focus();
                }
            }
        });
    });

    // Verification code submission
    document.getElementById('verifyCodeBtn').addEventListener('click', () => {
        const code = Array.from(codeInputs).map(input => input.value).join('');
        verifyCode(code);
    });

    function verifyCode(code) {
        fetch('/api/verify-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                clientId: selectedClientId,
                code: code
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSecurityQuestions();
            } else {
                // Show error animation
                codeInputs.forEach(input => {
                    input.classList.add('shake');
                    setTimeout(() => input.classList.remove('shake'), 500);
                });
            }
        });
    }

    function showSecurityQuestions() {
        fetch(`/api/security-questions/${selectedClientId}/`)
            .then(response => response.json())
            .then(questions => {
                const questionsContainer = document.getElementById('securityQuestions');
                questionsContainer.innerHTML = questions.map((q, index) => `
                    <div class="mb-3">
                        <label class="form-label">${q.question}</label>
                        <input type="text" class="form-control security-answer" data-question-id="${index}">
                    </div>
                `).join('');
                
                questionsContainer.innerHTML += `
                    <button class="btn btn-primary" id="verifyAnswersBtn">
                        Verificar Respuestas
                    </button>
                `;
                
                document.getElementById('codeVerification').classList.add('d-none');
                questionsContainer.classList.remove('d-none');
            });
    }

    // Helper function to get CSRF token
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

    // Update stepper progress
    function updateStepperProgress(step) {
        document.querySelectorAll('.step').forEach((el, index) => {
            if (index < step) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });
    }
}); 