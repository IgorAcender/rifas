/**
 * Gerenciador de Contador Regressivo de Reserva
 * Sincroniza com o servidor para garantir que o tempo seja sempre correto
 * mesmo se o usuário sair e voltar na página
 */

class ReservationCountdownManager {
    constructor(raffleId, containerId = 'countdown-container') {
        this.raffleId = raffleId;
        this.containerId = containerId;
        this.countdownInterval = null;
        this.expiresAt = null;
        this.hasActiveReservation = false;
    }

    /**
     * Inicia o gerenciador
     */
    async init() {
        console.log(`🕐 ReservationCountdownManager iniciado para raffle ${this.raffleId}`);
        
        // Verificar status inicial
        await this.checkReservationStatus();
        
        // Atualizar status a cada 10 segundos
        setInterval(() => this.checkReservationStatus(), 10000);
    }

    /**
     * Verifica o status de reserva com o servidor
     */
    async checkReservationStatus() {
        try {
            const response = await fetch(
                `/api/raffles/${this.raffleId}/reservation-status/`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include' // Incluir cookies de autenticação
                }
            );

            if (!response.ok) {
                console.warn(`⚠️ Erro ao verificar reserva: ${response.status}`);
                return;
            }

            const data = await response.json();
            
            if (data.has_active_reservation) {
                console.log(`✅ Reserva ativa encontrada. Tempo restante: ${data.time_remaining_seconds}s`);
                this.expiresAt = new Date(data.expires_at);
                this.hasActiveReservation = true;
                
                // Começar/reiniciar o countdown
                this.startCountdown();
            } else {
                console.log(`❌ Nenhuma reserva ativa`);
                this.hasActiveReservation = false;
                this.stopCountdown();
                this.hideCountdown();
            }
        } catch (error) {
            console.error('❌ Erro ao verificar status de reserva:', error);
        }
    }

    /**
     * Inicia o countdown visual
     */
    startCountdown() {
        // Parar countdown anterior se existir
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
        }

        // Mostrar contador
        this.showCountdown();

        // Atualizar a cada segundo
        this.countdownInterval = setInterval(() => {
            this.updateCountdown();
        }, 1000);

        // Atualizar imediatamente
        this.updateCountdown();
    }

    /**
     * Para o countdown
     */
    stopCountdown() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
    }

    /**
     * Atualiza o display do countdown
     */
    updateCountdown() {
        if (!this.expiresAt) {
            this.hideCountdown();
            return;
        }

        const now = new Date();
        const remaining = Math.floor((this.expiresAt - now) / 1000);

        if (remaining <= 0) {
            // Expirou
            this.onCountdownExpired();
            return;
        }

        // Converter para minutos e segundos
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;

        // Atualizar display
        this.updateCountdownDisplay(minutes, seconds);

        // Alertar se tempo curto
        if (remaining < 300) { // Menos de 5 minutos
            this.setCountdownStyle('warning');
        } else if (remaining < 60) { // Menos de 1 minuto
            this.setCountdownStyle('danger');
        } else {
            this.setCountdownStyle('normal');
        }
    }

    /**
     * Atualiza o elemento de countdown no DOM
     */
    updateCountdownDisplay(minutes, seconds) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        const timeElement = container.querySelector('[data-countdown-time]');
        
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }

    /**
     * Altera o estilo do countdown
     */
    setCountdownStyle(style) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.classList.remove('countdown-normal', 'countdown-warning', 'countdown-danger');
        container.classList.add(`countdown-${style}`);
    }

    /**
     * Mostra o elemento de countdown
     */
    showCountdown() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.style.display = 'block';
        }
    }

    /**
     * Esconde o elemento de countdown
     */
    hideCountdown() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.style.display = 'none';
        }
    }

    /**
     * Chamado quando o countdown expira
     */
    onCountdownExpired() {
        console.log('⏰ Reserva expirada!');
        this.stopCountdown();
        this.hideCountdown();
        
        // Mostrar alerta
        this.showExpiredAlert();
        
        // Recarregar página após 3 segundos
        setTimeout(() => {
            location.reload();
        }, 3000);
    }

    /**
     * Mostra alerta de expiração
     */
    showExpiredAlert() {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'reservation-expired-alert';
        alertDiv.innerHTML = `
            <div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 6px; padding: 16px; color: #dc2626; margin-bottom: 20px; text-align: center;">
                <strong>⏰ Sua reserva expirou!</strong><br>
                <small>Os números foram liberados. Você será redirecionado...</small>
            </div>
        `;
        
        // Inserir no início da página
        const mainContent = document.querySelector('main') || document.querySelector('.container') || document.body;
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
    }
}

/**
 * Inicializar automaticamente quando a página carregar
 */
document.addEventListener('DOMContentLoaded', function() {
    // Procurar por elemento que indique qual é o raffle ID
    const raffleIdElement = document.querySelector('[data-raffle-id]');
    
    if (raffleIdElement) {
        const raffleId = raffleIdElement.getAttribute('data-raffle-id');
        const manager = new ReservationCountdownManager(raffleId);
        manager.init();
        
        // Armazenar globalmente para acesso de outras partes do código
        window.reservationManager = manager;
    }
});
