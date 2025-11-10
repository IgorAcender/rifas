// Step navigation
function nextStep(step) {
    // Hide all sections
    document.querySelectorAll('.form-section').forEach(section => {
        section.classList.remove('active');
    });

    // Show target section
    document.querySelector(`[data-step="${step}"]`).classList.add('active');

    // Update steps indicator
    document.querySelectorAll('.step').forEach((stepEl, index) => {
        if (index < step) {
            stepEl.classList.add('active');
        } else {
            stepEl.classList.remove('active');
        }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function prevStep(step) {
    nextStep(step);
}

// Image preview
function previewImage(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = input.parentElement.querySelector('.image-preview');
            const placeholder = input.parentElement.querySelector('.upload-placeholder');

            preview.src = e.target.result;
            preview.style.display = 'block';
            placeholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

// Calculate estimate
function calculateEstimate() {
    const totalNumbers = document.getElementById('total_numbers').value;
    const pricePerNumber = document.getElementById('price_per_number').value;
    const feePercentage = parseFloat(document.getElementById('fee_percentage')?.value || 0);

    if (totalNumbers && pricePerNumber) {
        const total = parseFloat(totalNumbers) * parseFloat(pricePerNumber);
        const tax = total * (feePercentage / 100);

        document.querySelector('.estimate-value').textContent =
            `R$ ${total.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

        document.querySelector('.tax-value').textContent =
            `R$ ${tax.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
}

// Tax table removed - now using fee_percentage field

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Calculate on input change
    document.getElementById('total_numbers')?.addEventListener('change', calculateEstimate);
    document.getElementById('price_per_number')?.addEventListener('input', calculateEstimate);
    document.getElementById('fee_percentage')?.addEventListener('input', calculateEstimate);

    // Botão criar campanha na sidebar
    document.querySelector('.btn-criar-campanha')?.addEventListener('click', function() {
        window.location.href = '/criar-campanha';
    });
});
