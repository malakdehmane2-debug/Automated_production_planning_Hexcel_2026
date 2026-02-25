// Fonctions globales
function afficherNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.getElementById('notifications').appendChild(notification);
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function rafraichirDonnees() {
    location.reload();
}

function exporterPlanning() {
    const format = prompt('Format d\'export (excel/csv):', 'excel');
    if (!format) return;
    
    fetch('/api/planning/export', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            format: format,
            planning: window.currentPlanning || {}
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            afficherNotification(data.message, 'success');
            // Télécharger le fichier
            window.location.href = `/exports/${data.filename.split('/').pop()}`;
        } else {
            afficherNotification(data.message, 'error');
        }
    })
    .catch(error => {
        afficherNotification('Erreur lors de l\'export', 'error');
    });
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Charger les données initiales
    console.log('Application Flask prête !');
});