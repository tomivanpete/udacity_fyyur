const venueDeleteButton = document.getElementById('delete-venue-btn');
if (venueDeleteButton != null) {
    venueDeleteButton.onclick = function(e) {
        if (confirm('Are you sure you want to delete this venue?')) {
            const venueId = e.target.dataset.id;
            fetch('/venues/' + venueId, {
                method: 'DELETE',
            })
            .then(
                function() {
                    document.location.href = '/';
                }
            )
        }
    }
}

const artistDeleteButton = document.getElementById('delete-artist-btn');
if (artistDeleteButton != null) {
    artistDeleteButton.onclick = function(e) {
        if (confirm('Are you sure you want to delete this artist?')) {
            const artistId = e.target.dataset.id;
            fetch('/artists/' + artistId, {
                method: 'DELETE',
            })
            .then(
                function() {
                    document.location.href = '/';
                }
            )
        }
    }
}