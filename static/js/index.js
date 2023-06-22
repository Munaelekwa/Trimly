
document.addEventListener('DOMContentLoaded', function () {
    var navbarToggler = document.getElementById('navbar-toggler');
    var navbarMenu = document.getElementById('navbar-menu');
    var toggleButton = document.querySelector('.toggle-button');
    var sidebar = document.querySelector('.side');
	var createNew = document.getElementById('create-new-button');
	var option = document.getElementById('create-new-options');

	if (navbarToggler && navbarMenu) {
		navbarToggler.addEventListener('click', function () {
			navbarMenu.classList.toggle('show');
		});
	};

	if (toggleButton && sidebar) {
		toggleButton.addEventListener('click', function () {
			console.log('Toggle button clicked');
			sidebar.classList.toggle('side-show');
		});
	};


	if (createNew && option) {
		createNew.addEventListener('click', function () {
			option.classList.toggle('options-show');
		});
	}

	document.querySelectorAll('.close-button').forEach(function(button) {
		button.addEventListener('click', function() {
		  this.parentNode.parentNode.remove();
		});
	  });


  });



