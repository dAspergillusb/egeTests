const oneAnsQ = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '22', '23', '24'];
const oneAnsQFiles = ['3', '9', '10', '22', '24'];
const twoAnsQFiles = ['17', '18', '26'];
const manyAnsQ = '25';
const manyAnsQFiles = '27';
const specialQ = '19';

function removeFields() {
    var fields = document.getElementById('fields');
    fields.replaceChildren();
}

function createFields() {
    var fields = document.createElement('div');
    fields.id = 'fields';
    
    var box = document.getElementById('box');
    box.appendChild(fields);
}

function createForm() {
    let fields = document.getElementById('fields');
    let form = document.createElement('form');
    form.setAttribute('id', 'form');
    form.setAttribute('enctype', 'multipart/form-data');
    fields.appendChild(form);
}

function createDiffField(difficulty = '') {
    const difficulties = ['Базовый', 'Средний', 'Сложный'];
    var form = document.getElementById('form');
    
    var label = document.createElement('label');
    label.className = 'mb-3 h4';
    label.innerText = 'Выберете сложность для вопроса:';
    form.appendChild(label);
    
    var diff = document.createElement('select');
    diff.className = 'mb-5 form-select';
    diff.id = 'q_difficulty';
    diff.name = 'q_difficulty';
    form.appendChild(diff);
    
    for (let i = 1; i <=3; i++) {
        var option = document.createElement('option');
        option.id = difficulties[i - 1];
        option.value = difficulties[i - 1];
        option.innerText = difficulties[i - 1];
        diff.appendChild(option);
    }
    if (difficulty) {
        diff.selectedIndex = difficulties.indexOf(difficulty);
    }
}

function createTextArea(areaIdName, qType) {
    var form = document.getElementById('form');
    
    var label = document.createElement('label');
    label.className = 'mb-3 h4';
    label.innerText = `Введите содержимое вопроса (задание ${qType}):`;
    form.appendChild(label);
    
    var textArea = document.createElement('textarea');
    textArea.id = areaIdName;
    textArea.className = 'ckeditor';
    textArea.name = areaIdName;
    form.appendChild(textArea);
	return textArea;
}

function createFiles() {
    const filesId = ['file_one', 'file_two', 'file_three', 'file_four'];
    var form = document.getElementById('form');
    
    var label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте файлы (один или несколько):';
    form.appendChild(label);
    
    for (let i = 0; i <= 3; i++) {
        var inputFile = document.createElement('input');
        inputFile.type = 'file';
        inputFile.className = 'form-control mb-5 ms-4 mt-3 w-90';
        inputFile.id = filesId[i];
        inputFile.name = filesId[i];
        inputFile.setAttribute('ariaDescribedByElements', 'inputGroupFileAddon04');
        inputFile.ariaLabel = 'Upload';
        form.appendChild(inputFile);
    }
}

function createOneAnswer(answers, specNum = '') {
    var form = document.getElementById('form');
    
    var label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте правильный ответ:';
    form.appendChild(label);
    
    var input = document.createElement('input');
    input.className = 'form-control w-75 mb-3';
    input.type = 'text';
    if (!specNum) {
        input.name = 'q_right_answer';
        input.id = 'q_right_answer';
    } else {
        input.name = `q_right_answer_${specNum}`;
        input.id = `q_right_answer_${specNum}`;
    }
    if (answers[0]) {
        input.value = answers[0];
    } else {
        input.value = '';
    }
    form.appendChild(input);
}

function createTwoAnswers(answers, specNum = '') {
    var form = document.getElementById('form');
    
    var label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте правильные ответы:';
    form.appendChild(label);

    var div = document.createElement('div');
    div.className = 'input-group w-75 mb-3';
    form.appendChild(div);

    var span = document.createElement('span');
    span.className = 'input-group-text';
    span.setAttribute('style', 'width:200px;');
    span.innerHTML = 'Пара ответов';
    div.appendChild(span);

    for (let i = 1; i <= 2; i++) {
        let input = document.createElement('input');
        input.className = 'form-control';
        input.type = 'text';
        if (!specNum) {
            input.name = `q_right_answer_${i.toString()}`;
            input.id = `q_right_answer_${i.toString()}`;
        } else {
            input.name = `q_right_answer_${specNum}_${i.toString()}`;
            input.id = `q_right_answer_${specNum}_${i.toString()}`;
        }
        input.setAttribute('aria-label', `${i}`);
        if (answers[i - 1]) {
            input.value = answers[i - 1];
        } else {
            input.value = '';
        }
        div.appendChild(input);
    }
}

function createManyAnswers(answers, value = 17) {
    const q_nums = [
            'q_right_answer_1',
            'q_right_answer_2',
            'q_right_answer_3',
            'q_right_answer_4',
            'q_right_answer_5',
            'q_right_answer_6',
            'q_right_answer_7',
            'q_right_answer_8',
            'q_right_answer_9',
            'q_right_answer_10',
            'q_right_answer_11',
            'q_right_answer_12',
            'q_right_answer_13',
            'q_right_answer_14',
            'q_right_answer_15',
            'q_right_answer_16',
            'q_right_answer_17',
            'q_right_answer_18',
    ];
    const spanNames = [
            'Первая пара ответов',
            'Вторая пара ответов',
            'Третья пара ответов',
            'Четвёртая пара ответов',
            'Пятая пара ответов',
            'Шестая пара ответов',
            'Седьмая пара ответов',
            'Восьмая пара ответов',
            'Девятая пара ответов'
    ];
    let form = document.getElementById('form');
    
    let label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте правильные ответы:';
    form.appendChild(label);
    
    let qPairNum = 0
    for (let i = 1; i <= value; i += 2) {
        var div = document.createElement('div');
        div.className = 'input-group w-75';
        form.appendChild(div);
        
        var span = document.createElement('span');
        span.className = 'input-group-text';
		span.setAttribute('style', 'width:210px;');
        span.innerText = spanNames[qPairNum];
        div.appendChild(span);
        qPairNum++;
        
        for (let j = 0; j <= 1; j++) {
            var input = document.createElement('input');
            input.type = 'text';
            input.ariaLabel = (i + j).toString();
            input.className = 'form-control';
            input.id = `q_right_answer_${(i + j).toString()}`;
            input.name = `q_right_answer_${(i + j).toString()}`;
            if (answers[i + j - 1]) {
                input.value = answers[i + j - 1];
            } else {
                input.value = '';
            }
            div.appendChild(input);
        }
    }
    div.className += ' mb-3';
}

function createButtonSave(functionName) {
	let form = document.getElementById('form');

    let buttonDiv = document.createElement('div');
    buttonDiv.setAttribute('class', 'd-grid gap-2 d-md-block');

    let button = document.createElement('button');
    button.setAttribute('class', 'btn btn-secondary py-2 mb-2');
    button.setAttribute('type', 'button');
    button.setAttribute('onclick', `${functionName}`);
    button.innerHTML = 'Сохранить';

    buttonDiv.appendChild(button);
    form.appendChild(buttonDiv);
}

function createColorLine(size = '10', color = 'blue') {
    let form = document.getElementById('form');
    let line = document.createElement('hr');
    line.setAttribute('size', size);
    line.setAttribute('color', color);
    line.setAttribute('class', 'mb-3');
    form.appendChild(line);
}

function createQTypeFields(
    selectValue,
    difficulty = '',
    datas = ['', '', ''],
    forCreate = true,
    answers = null
) {
    answers = answers ?? [];
	if (window.editorInstance) {
		window.editorInstance.destroy();
	}
	if (window.editorInstanceTwo) {
		window.editorInstanceTwo.destroy();
	}
	if (window.editorInstanceThree) {
		window.editorInstanceThree.destroy();
	}
    removeFields();
    createForm();
    createDiffField(difficulty);
    
	if (selectValue != specialQ) {
		var textArea = createTextArea('q_text', selectValue);
        window.loadCKEditor(textArea, 0, datas[0]);
	}
    if (oneAnsQ.includes(selectValue)) {
        if (oneAnsQFiles.includes(selectValue)) {
            createFiles();
        }
		createOneAnswer(answers);
	} else if (twoAnsQFiles.includes(selectValue)) {
		createFiles();
		createTwoAnswers(answers);
	} else if (selectValue == manyAnsQ) {
		createManyAnswers(answers);
	} else if (selectValue == manyAnsQFiles) {
		createFiles();
		createManyAnswers(answers, 3);
	} else if (selectValue == specialQ) {
		let textAreaNineteen = createTextArea('q_text_19', '19');
        if (answers[0]) {
            createOneAnswer(answers[0], '19');
        } else {
            createOneAnswer(answers, '19');
        }
        window.loadCKEditor(textAreaNineteen, 0, datas[0]);
        createColorLine('5', 'black')

        let textAreaTwenty = createTextArea('q_text_20', '20');
        if (answers[1]) {
            createTwoAnswers(answers[1], '20');
        } else {
            createTwoAnswers(answers, '20');
        }
        window.loadCKEditor(textAreaTwenty, 1, datas[1]);
        createColorLine('5', 'black')

        let textAreaTwentyOne = createTextArea('q_text_21', '21');
        if (answers[2]) {
            createOneAnswer(answers[2], '21');
        } else {
            createOneAnswer(answers, '21');
        }
        window.loadCKEditor(textAreaTwentyOne, 2, datas[2]);
	}
    if (forCreate) {
        createColorLine();
        if (selectValue != specialQ) {
            createButtonSave(`getDataToSave(${selectValue})`)
        } else {
            createButtonSave(`getDataToSave1921()`)
        }
    }
}
