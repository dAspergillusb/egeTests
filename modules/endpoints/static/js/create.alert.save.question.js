function createMainDiv() {
	var mainDiv = document.createElement('div');
	mainDiv.id = 'mainDiv';
	mainDiv.className = 'position-fixed bottom-0 end-0 p-3';
	mainDiv.Style = 'z-index:11';
	return mainDiv;
}

function createDivAlert(result) {
	var divAlert = document.createElement('div');
	var divAlertButton = document.createElement('button');
	divAlert.id = 'alert';
	divAlert.className = 'alert alert-dismissible fade show';
	divAlert.setAttribute('role', 'alert');
	if (result) {
	    divAlert.textContent = 'Ваш вопрос успешно сохранён!';
	    divAlert.className += ' alert-success';
	} else if (!result) {
	    divAlert.textContent = 'В форме есть ошибки или такой вопрос есть в базе!';
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

function timerAlert() {
	const button = document.getElementById('button');
	const mainDiv = document.getElementById('mainDiv');
	if (button) {
		button.click();
	}
	if (mainDiv) {
		mainDiv.remove();
	}
}

function createAlert(result) {
	var div = document.getElementById('fields');
	var divMain = createMainDiv();
	var divAlert = createDivAlert(result);
	divMain.appendChild(divAlert);
	div.appendChild(divMain);
	setTimeout(timerAlert, 3000);
}
