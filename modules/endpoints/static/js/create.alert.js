const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function createMainDiv() {
	let mainDiv = document.createElement('div');
	mainDiv.id = 'mainDiv';
	mainDiv.className = 'position-fixed bottom-0 end-0 p-3';
	mainDiv.Style = 'z-index:11';
	return mainDiv;
}

function createDivAlert(result, messages) {
	let divAlert = document.createElement('div');
	let divAlertButton = document.createElement('button');
	divAlert.id = 'alert';
	divAlert.className = 'alert alert-dismissible fade';
	divAlert.setAttribute('role', 'alert');
	if (result) {
	    divAlert.innerHTML = messages[0];
	    divAlert.className += ' alert-success';
	} else if (!result) {
	    divAlert.innerHTML = messages[1];
	    divAlert.className += ' alert-warning';
	} else {
	    divAlert.innerHTML = 'Что-то пошло не так! Попробуйте попозже.';
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

async function timerAlert() {
	const button = document.getElementById('button');
	const mainDiv = document.getElementById('mainDiv');
	await sleep(100);
	mainDiv.querySelector('div[id="alert"]').classList.remove('show');
	// if (button) {
	// 	button.click();
	// }
	await sleep(150);
	if (mainDiv) {
		mainDiv.remove();
	}
}

async function createAlert(result, messages) {
	let div = document.querySelector('main');
	let divMain = createMainDiv();
	let divAlert = createDivAlert(result, messages);
	divMain.appendChild(divAlert);
	div.appendChild(divMain);
	await sleep(100);
	divAlert.classList.add('show');
	setTimeout(timerAlert, 3000);
}
