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

    if (totalNumbers && pricePerNumber) {
        const total = parseFloat(totalNumbers) * parseFloat(pricePerNumber);
        const tax = calculateTax(total);

        document.querySelector('.estimate-value').textContent =
            `R$ ${total.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

        document.querySelector('.tax-value').textContent =
            `R$ ${tax.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
}

// Tax table (baseado no Rifa321)
function calculateTax(total) {
    const taxes = [
        { from: 0.01, to: 100, fee: 7 },
        { from: 101, to: 250, fee: 17 },
        { from: 251, to: 450, fee: 27 },
        { from: 451, to: 750, fee: 37 },
        { from: 751, to: 1000, fee: 47 },
        { from: 1001, to: 2000, fee: 67 },
        { from: 2001, to: 4000, fee: 77 },
        { from: 4001, to: 7000, fee: 97 },
        { from: 7001, to: 10000, fee: 147 },
        { from: 10001, to: 15000, fee: 197 },
        { from: 15001, to: 20000, fee: 247 },
        { from: 20001, to: 30000, fee: 347 },
        { from: 30001, to: 50000, fee: 697 },
        { from: 50001, to: 70000, fee: 797 },
        { from: 70001, to: 100000, fee: 997 },
        { from: 100001, to: Infinity, fee: 1497 }
    ];

    const taxBracket = taxes.find(t => total >= t.from && total <= t.to);
    return taxBracket ? taxBracket.fee : 0;
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Calculate on input change
    document.getElementById('total_numbers')?.addEventListener('change', calculateEstimate);
    document.getElementById('price_per_number')?.addEventListener('input', calculateEstimate);

    // Botão criar campanha na sidebar
    document.querySelector('.btn-criar-campanha')?.addEventListener('click', function() {
        window.location.href = '/criar-campanha';
    });
});
