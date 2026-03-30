// Fonction pour générer l'ordonnancement
function genererOrdonnancement() {
    fetch('/api/generer_ordonnancement', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Afficher une notification de succès
            afficherNotification('Ordonnancement généré avec succès', 'success');
            // Recharger la page pour afficher les mises à jour
            setTimeout(() => location.reload(), 1500);
        } else {
            throw new Error(data.message || 'Erreur lors de la génération');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        afficherNotification(error.message || 'Une erreur est survenue', 'error');
    });
}

// Fonction pour signaler une absence
function signalerAbsence() {
    // Implémentez la logique de signalement d'absence ici
    afficherNotification('Fonctionnalité de signalement d\'absence à implémenter', 'info');
}

// Fonction pour afficher le planning
function voirPlanning() {
    // Implémentez la logique d'affichage du planning ici
    afficherNotification('Fonctionnalité de visualisation du planning à implémenter', 'info');
}

// Fonction pour exporter le planning
function exporterPlanning() {
    // Implémentez la logique d'exportation ici
    afficherNotification('Fonctionnalité d\'exportation du planning à implémenter', 'info');
}

// Fonction pour naviguer vers la page du projet sélectionné
function naviguerVersProjet() {
    const select = document.getElementById('selectProjet');
    const value = select.value;
    
    if (value) {
        const [zoneId, projetId] = value.split('-');
        // Réinitialiser la sélection avant de naviguer
        select.value = '';
        // Naviguer vers la page du projet
        window.location.href = `/zone/${zoneId}/projet/${projetId}/ordonnancement`;
    }
}

// Initialisation du tableau de bord
document.addEventListener('DOMContentLoaded', function() {
    console.log('Tableau de bord initialisé');
});