document.addEventListener('DOMContentLoaded', function () {
  const typeSelect = document.getElementById('level1');
  const genreSelect = document.getElementById('level2');
  const instrumentSelect = document.querySelector('select[name="instrument"]');

  const data = [
      ["Vocalist", "Blues", "Alto"],
      ["Vocalist", "Blues", "Soprano"],
      ["Vocalist", "Blues", "Tenor"],
      ["Vocalist", "Bollywood", "Alto"],
      ["Vocalist", "Bollywood", "Bass"],
      ["Vocalist", "Bollywood", "Soprano"],
      ["Vocalist", "Bollywood", "Tenor"],
      ["Vocalist", "Carnatic", "Alto"],
      ["Vocalist", "Carnatic", "Bass"],
      ["Vocalist", "Carnatic", "Soprano"],
      ["Vocalist", "Carnatic", "Tenor"],
      ["Vocalist", "Classical", "Alto"],
      ["Vocalist", "Classical", "Bass"],
      ["Vocalist", "Classical", "Soprano"],
      ["Vocalist", "Classical", "Tenor"],
      ["Vocalist", "Folk", "Alto"],
      ["Vocalist", "Folk", "Soprano"],
      ["Vocalist", "Folk", "Tenor"],
      ["Vocalist", "Ghazal", "Alto"],
      ["Vocalist", "Ghazal", "Soprano"],
      ["Vocalist", "Ghazal", "Tenor"],
      ["Vocalist", "Gospel", "Alto"],
      ["Vocalist", "Gospel", "Soprano"],
      ["Vocalist", "Gospel", "Tenor"],
      ["Vocalist", "Hip-Hop", "Alto"],
      ["Vocalist", "Hip-Hop", "Soprano"],
      ["Vocalist", "Hip-Hop", "Tenor"],
      ["Vocalist", "Indie", "Alto"],
      ["Vocalist", "Indie", "Soprano"],
      ["Vocalist", "Indie", "Tenor"],
      ["Vocalist", "Jazz", "Alto"],
      ["Vocalist", "Jazz", "Bass"],
      ["Vocalist", "Jazz", "Soprano"],
      ["Vocalist", "Jazz", "Tenor"],
      ["Vocalist", "Metal", "Alto"],
      ["Vocalist", "Metal", "Soprano"],
      ["Vocalist", "Metal", "Tenor"],
      ["Vocalist", "Pop", "Alto"],
      ["Vocalist", "Pop", "Bass"],
      ["Vocalist", "Pop", "Soprano"],
      ["Vocalist", "Pop", "Tenor"],
      ["Vocalist", "Rock", "Alto"],
      ["Vocalist", "Rock", "Bass"],
      ["Vocalist", "Rock", "Soprano"],
      ["Vocalist", "Rock", "Tenor"],
      ["Vocalist", "Indi-pop", "Alto"],
      ["Vocalist", "Indi-pop", "Soprano"],
      ["Vocalist", "Indi-pop", "Tenor"],
      ["Instrumentalist", "Blues", "Sitar"],
      ["Instrumentalist", "Blues", "Tabla"],
      ["Instrumentalist", "Bollywood", "Bass"],
      ["Instrumentalist", "Bollywood", "Drums"],
      ["Instrumentalist", "Bollywood", "Guitar"],
      ["Instrumentalist", "Bollywood", "Piano"],
      ["Instrumentalist", "Bollywood", "Saxophone"],
      ["Instrumentalist", "Carnatic", "Flute"],
      ["Instrumentalist", "Carnatic", "Mridangam"],
      ["Instrumentalist", "Carnatic", "Sitar"],
      ["Instrumentalist", "Carnatic", "Veena"],
      ["Instrumentalist", "Carnatic", "Violin"],
      ["Instrumentalist", "Classical", "Cello"],
      ["Instrumentalist", "Classical", "Clarinet"],
      ["Instrumentalist", "Classical", "Flute"],
      ["Instrumentalist", "Classical", "Piano"],
      ["Instrumentalist", "Classical", "Violin"],
      ["Instrumentalist", "Ghazal", "Flute"],
      ["Instrumentalist", "Ghazal", "Sitar"],
      ["Instrumentalist", "Ghazal", "Tabla"],
      ["Instrumentalist", "Hindustani", "Flute"],
      ["Instrumentalist", "Hindustani", "Sarangi"],
      ["Instrumentalist", "Hindustani", "Sitar"],
      ["Instrumentalist", "Hindustani", "Tabla"],
      ["Instrumentalist", "Jazz", "Bass"],
      ["Instrumentalist", "Jazz", "Drums"],
      ["Instrumentalist", "Jazz", "Guitar"],
      ["Instrumentalist", "Jazz", "Piano"],
      ["Instrumentalist", "Jazz", "Saxophone"],
      ["Instrumentalist", "Jazz", "Trombone"],
      ["Instrumentalist", "Jazz", "Trumphet"],
      ["Instrumentalist", "Pop", "Bass"],
      ["Instrumentalist", "Pop", "Drums"],
      ["Instrumentalist", "Pop", "Guitar"],
      ["Instrumentalist", "Pop", "Keyboard"],
      ["Instrumentalist", "Pop", "Piano"],
      ["Instrumentalist", "Pop", "Saxophone"],
     ];

  // Update genre and instrument options based on selected type
  typeSelect.addEventListener('change', function() {
    const selectedType = typeSelect.value;
    const genres = Array.from(new Set(data.filter(item => item[0] === selectedType).map(item => item[1])));
   
    genreSelect.innerHTML = '<option value="" disabled selected>Genre</option>';
    genres.forEach(genre => {
      const option = document.createElement('option');
      option.value = genre;
      option.textContent = genre;
      genreSelect.appendChild(option);
    });
   
    // Clear instrument select options when type changes
    instrumentSelect.innerHTML = '';
  });

  // Update instrument options based on selected genre
  genreSelect.addEventListener('change', function() {
    const selectedType = typeSelect.value;
    const selectedGenre = genreSelect.value;
    const instruments = data.filter(item => item[0] === selectedType && item[1] === selectedGenre).map(item => item[2]);

    instrumentSelect.innerHTML = '';
    instruments.forEach(instrument => {
      const option = document.createElement('option');
      option.value = instrument;
      option.textContent = instrument;
      instrumentSelect.appendChild(option);
    });
  });
});

document.addEventListener("DOMContentLoaded", function() {
  const form = document.querySelector('form'); // The registration form
  const passwordField = document.querySelector('input[name="password"]');
  const confirmPasswordField = document.querySelector('input[name="confirm_password"]');

  form.addEventListener('submit', function(event) {
      // Check if the passwords match
      if (passwordField.value !== confirmPasswordField.value) {
          event.preventDefault(); // Prevent form submission
          alert("Passwords do not match! Please confirm that both passwords are the same.");
         
          // Preserve the form data, no reset will happen now.
          // You can also add custom logic to highlight the password fields if needed.
      }
  });
});
