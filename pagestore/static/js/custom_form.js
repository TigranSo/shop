document.addEventListener('DOMContentLoaded', function() {
  var usernameField = document.getElementById('id_username');

  if (usernameField) {
    var helpText = 'Username (letters, digits and @/./+/-/_)';

    usernameField.addEventListener('mouseover', function() {
      usernameField.setAttribute('placeholder', helpText);
    });

    usernameField.addEventListener('mouseout', function() {
      usernameField.removeAttribute('placeholder');
    });
  }
});