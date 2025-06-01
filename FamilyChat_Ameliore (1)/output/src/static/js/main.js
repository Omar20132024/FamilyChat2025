// Fichier JavaScript principal pour FamilyChat

// Gestion du menu mobile
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Fermer le menu en cliquant à l'extérieur
    document.addEventListener('click', function(event) {
        if (sidebar && sidebar.classList.contains('active') && !sidebar.contains(event.target) && event.target !== menuToggle) {
            sidebar.classList.remove('active');
        }
    });
    
    // Gestion des alertes
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 500);
        }, 5000);
    });
    
    // Initialisation des WebSockets
    if (typeof io !== 'undefined') {
        const socket = io();
        
        // Événement de connexion
        socket.on('connect', function() {
            console.log('Connecté au serveur WebSocket');
        });
        
        // Événement de déconnexion
        socket.on('disconnect', function() {
            console.log('Déconnecté du serveur WebSocket');
        });
        
        // Événement d'erreur
        socket.on('error', function(error) {
            console.error('Erreur WebSocket:', error);
        });
    }
});

// Fonction pour afficher la date et l'heure
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Fonction pour formater les messages
function formatMessage(message) {
    // Détection des liens
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return message.replace(urlRegex, url => `<a href="${url}" target="_blank">${url}</a>`);
}

// Fonction pour scroller automatiquement vers le bas
function scrollToBottom(element) {
    if (element) {
        element.scrollTop = element.scrollHeight;
    }
}
