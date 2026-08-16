function showHideInf(elementId) {
	inf = document.getElementById('information');
	infButton = document.getElementById('inf');
	if (elementId == 'information') {
		inf.hidden = false;
		infButton.className = 'btn btn-primary';
		mainDiv = document.getElementById('main');
		mainDiv.replaceChildren();
	} else {
		inf.hidden = true;
		infButton.className = 'btn btn-outline-primary';
	}
	buttons = document.querySelectorAll('[name="navButton"]');
	for (const button of buttons) {
		if (button.id == elementId) {
			button.className = button.className.replace('btn-outline-primary', 'btn-primary');
		} else {
			button.className = button.className.replace('btn-primary', 'btn-outline-primary');
		}
	}
 }
	  
function putQuestionData(questionData) {
	mainDiv = document.getElementById('main');
	mainDiv.replaceChildren();
	mainDiv.appendChild(putQuestionText(questionData.q_text));
	if (questionData.q_files) {
	mainDiv.appendChild(putQuestionFiles(questionData.q_number, questionData.q_files));
	};
	mainDiv.appendChild(putQuestionAnswers(questionData.q_number, questionData.q_right_answer, questionData.answers));
	mainDiv.appendChild(putSaveAnswerButton(questionData.q_number));
	mainDiv.appendChild(putAlertDiv(questionData.q_number));
	if (questionData.answers != '0') {
		changeButtonToSaved();
	}
	
	var inputs = document.querySelectorAll(`[name="q_${questionData.q_number}"]`);
	var saveButton = document.querySelector('[name="saveAnswerButton"]');
	inputs.forEach(input => {
		input.addEventListener('input', (event) => {
			saveButton.removeAttribute('disabled');
			saveButton.innerHTML = 'Сохранить ответ';
			saveButton.className = 'btn btn-outline-primary mb-4';
		});
	});
}

function putQuestionText(qText) {
	var qTextDiv = document.createElement('div');
	var qTextH = document.createElement('h1');
	
	qTextDiv.className = 'ck-content question-block';
	qTextH.className = 'h4 fw-normal lh-base';
	qTextH.innerHTML = qText;
	
	qTextDiv.appendChild(qTextH);
	return qTextDiv;
}

function putQuestionFiles(qNum, qFiles) {
	var qFilesDiv = document.createElement('div');
	
	qFilesDiv.className = 'container-fluid mb-4';
	
	if (qNum == 27) {
		var types = ['A', 'B'];
		var type_index = 0;
	}
	
	for (const file of qFiles.split('&')) {
		var qFilesA = document.createElement('a');
		qFilesA.className = 'mb-2 ms-4 h4';
		qFilesA.href = file.replace('//', '/');
		qFilesA.setAttribute('download', '');
		var end = file.split(".").slice(-1);
		if (qNum == 27) {
			qFilesA.innerHTML = `${qNum}-${types[type_index]}.${end}`;
			type_index++;
		} else {
			qFilesA.innerHTML = `${qNum}.${end}`;
		}
		qFilesDiv.appendChild(qFilesA);
	}
	return qFilesDiv;
}

function putQuestionAnswers(qNum, answersValue, oldAnswers) {
	var qDiv = document.createElement('div');
	var infText = document.createElement('p');
	
	qDiv.className = 'form px-2 mb-4';
	infText.className = 'h5 ms-5 mb-4';
	infText.align = 'left';
	infText.innerHTML = 'Ответ здесь';
	
	qDiv.appendChild(infText);
	
	var answer = oldAnswers;
	if (answersValue == 1) {
		var answerInput = document.createElement('input');
		
		answerInput.type = 'text';
		answerInput.className = 'form-control mb-5 ms-4 mt-3 w-50';
		answerInput.id = `qOne${qNum}`;
		answerInput.name = `q_${qNum}`;
		answerInput.onchange = `isAnswered("qOne${qNum}", "${qNum}")`;
		
		if (answer != '0') {
			answerInput.value = answer;
		} else {
			answerInput.value = '';
		}
		qDiv.appendChild(answerInput);
	} else {
		var answers = answer.split('$');
		for (let i = 0; i < answersValue; i += 2) {
			var inputDiv = document.createElement('div');
			inputDiv.className = 'input-group w-50';
			inputDiv.id = `qMany${qNum}`;
			
			var inputOne = document.createElement('input');
			inputOne.type = 'text';
			inputOne.setAttribute('aria-label', i + 1);
			inputOne.className = 'form-control';
			inputOne.name = `q_${qNum}`;
			inputOne.id = `qMany${qNum}${i + 1}`;
			if (parseInt(answers.slice(i))) {
				inputOne.value = answers.at(i);
			} else {
				inputOne.value = '';
			}
			
			var inputTwo = document.createElement('input');
			inputTwo.type = 'text';
			inputTwo.setAttribute('aria-label', i + 2);
			inputTwo.className = 'form-control';
			inputTwo.name = `q_${qNum}`;
			inputTwo.id = `qMany${qNum}${i + 2}`;
			if (parseInt(answers.slice(i + 1))) {
				inputTwo.value = answers.at(i + 1);
			} else {
				inputTwo.value = '';
			}
			inputDiv.appendChild(inputOne);
			inputDiv.appendChild(inputTwo);
			qDiv.appendChild(inputDiv);
		}
	}
	return qDiv;
}

function putSaveAnswerButton(qNum) {
	var saveButton = document.createElement('button');
	
	saveButton.className = 'btn btn-outline-primary mb-4';
	saveButton.name = 'saveAnswerButton';
	saveButton.setAttribute('onclick', `sendAnswer('q_${qNum}', 'button_${qNum}')`);
	saveButton.setAttribute('type', 'button');
	saveButton.innerHTML = 'Сохранить ответ';
	return saveButton;
}

function putAlertDiv(qNum) {
	var alertDiv = document.createElement('div');
	
	alertDiv.setAttribute('id', `button_${qNum}`);
	return alertDiv;
}

function changeButtonToSaved() {
	var saveButton = document.querySelector('[name="saveAnswerButton"]');
	
	saveButton.innerHTML = 'Ответ сохранён';
	saveButton.className = 'btn btn-outline-success mb-4';
	saveButton.setAttribute('disabled', '');
}