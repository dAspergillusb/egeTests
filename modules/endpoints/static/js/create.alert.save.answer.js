function createMainDiv() {
	var mainDiv = document.createElement('div');
	mainDiv.id = 'mainDiv';
	mainDiv.className = 'position-fixed bottom-0 end-0 p-3';
	mainDiv.Style = 'z-index:11';
	return mainDiv;
}

function createDivAlert(result, qNavId) {
	var divAlert = document.createElement('div');
	var divAlertButton = document.createElement('button');
	divAlert.id = 'alert';
	divAlert.className = 'alert alert-dismissible fade show';
	divAlert.setAttribute('role', 'alert');
	if (result == 'true') {
	    divAlert.textContent = 'Ответ успешно сохранён!';
	    divAlert.className += ' alert-success';
	    var qNav = document.getElementById(qNavId);
	    qNav.classList.add('fw-bold', 'text-decoration-underline');
		changeButtonToSaved();
	} else if (result == 'false') {
	    divAlert.textContent = 'Сначала введите ответ!';
	    divAlert.className += ' alert-warning';
	} else {
	    divAlert.textContent = 'Что-то пошло не так! Попробуйте попозже.';
	    divAlert.className += ' alert-danger';
	}
	divAlertButton.type = 'button';
	divAlertButton.id = 'button';
	divAlertButton.className = 'btn-close';
	divAlertButton.setAttribute('data-bs-dismiss', 'alert');
	divAlertButton.setAttribute('aria-label', 'Закрыть');
	divAlert.appendChild(divAlertButton);
	return divAlert;
}

function createAlert(divId, result) {
	var div = document.getElementById(divId);
	var divMain = createMainDiv();
	var divAlert = createDivAlert(result, divId.split('_').slice(-1));
	divMain.appendChild(divAlert);
	div.appendChild(divMain);
}
