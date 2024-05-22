// Funkcja do filtrowania pracowników
function filterEmployees() {
    var selectedCompetences = $('#id_competences').val(); // Pobranie wybranych kompetencji
    $.ajax({
        url: '/filter-employees/', // Ścieżka URL do widoku filtrującego pracowników
        type: 'GET',
        data: { competences: selectedCompetences }, // Przekazanie wybranych kompetencji jako parametr
        success: function(data) {
            // Obsługa danych zwróconych z serwera
            console.log(data);
            // Wyczyść listę pracowników
            $('#filtered-employees').empty();
            // Dodaj pracowników do listy
            data.forEach(function(employee) {
                $('#filtered-employees').append('<li>' + employee.name + '</li>');
            });
        },
        error: function(error) {
            console.error('Error filtering employees:', error);
        }
    });
}
