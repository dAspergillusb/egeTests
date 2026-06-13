const oneAnsQ = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '23'];
const oneAnsQFiles = ['3', '9', '10', '22', '24'];
const twoAnsQFiles = ['17', '18', '26'];
const manyAnsQ = '25';
const manyAnsQFiles = '27';
const specialQ = '19';

function removeFields() {
    var fields = document.getElementById('fields');
    fields.replaceChildren();
};

function createFields() {
    var fields = document.createElement('div');
    fields.id = 'fields';
    
    var box = document.getElementById('box');
    box.appendChild(fields);
};

function createDiffField() {
    const difficulties = ['Базовый', 'Средний', 'Сложный'];
    var fields = document.getElementById('fields');
    
    var label = document.createElement('label');
    label.className = 'mb-3 h4';
    label.innerText = 'Выберете сложность для вопроса:';
    fields.appendChild(label);
    
    var diff = document.createElement('select');
    diff.className = 'mb-5 form-select';
    diff.id = 'q_difficulty';
    diff.name = 'q_difficulty';
    fields.appendChild(diff);
    
    for (let i = 1; i <=3; i++) {
        var option = document.createElement('option');
        option.id = difficulties[i - 1];
        option.value = difficulties[i - 1];
        option.innerText = difficulties[i - 1];
        diff.appendChild(option);
    };
};

function createTextArea(areaIdName, qType) {
    var fields = document.getElementById('fields');
    
    var label = document.createElement('label');
    label.className = 'mb-3 h4';
    label.innerText = 'Введите содержимое вопроса (задание ' + qType + '):';
    fields.appendChild(label);
    
    var textArea = document.createElement('textarea');
    textArea.id = areaIdName;
    textArea.className = 'ckeditor';
    textArea.name = areaIdName;
    fields.appendChild(textArea);
	return textArea;
};

function createFiles() {
    const filesId = ['file_one', 'file_two', 'file_three', 'file_four'];
    var fields = document.getElementById('fields');
    
    var label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте файлы (один или несколько):';
    fields.appendChild(label);
    
    for (let i = 1; i <= 4; i++) {
        var inputFile = document.createElement('input');
        inputFile.type = 'file';
        inputFile.className = 'form-control mb-5 ms-4 mt-3 w-90';
        inputFile.id = filesId[i];
        inputFile.name = filesId[i];
        inputFile.ariaDescribedByElements = 'inputGroupFileAddon04';
        inputFile.ariaLabel = 'Upload';
        fields.appendChild(inputFile);
    };    
};

function createOneAnswer() {
    var fields = document.getElementById('fields');
    
    var label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте правильный ответ:';
    fields.appendChild(label);
    
    var input = document.createElement('input');
    input.className = 'form-control w-75';
    input.type = 'text';
    input.name = 'q_right_answer';
    input.id = 'q_right_answer';
    input.value = '';
    fields.appendChild(input);
};

function createTwoAnswers() {
    var fields = document.getElementById('fields');
    
    var label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте правильные ответы:';
    fields.appendChild(label);
    
    var div = document.createElement('div');
    div.className = 'input-group w-75';
    fields.appendChild(div);
    
	var span = document.createElement('span');
	span.className = 'input-group-text';
	//span.setAttribute('style', 'width:230px;');
	span.innerHTML = 'Пара ответов';
	div.appendChild(span);
	
    for (let i = 1; i <= 2; i++) {
        var input = document.createElement('input');
        input.className = 'form-control';
        input.type = 'text';
        input.name = 'q_right_answer_' + i.toString();
        input.id = 'q_right_answer_' + i.toString();
		input.setAttribute('aria-label', 'i');
        input.value = '';
        div.appendChild(input);
    };
};

function createManyAnswers() {
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
    var fields = document.getElementById('fields');
    
    var label = document.createElement('label');
    label.className = 'mt-3 mb-3 h4';
    label.innerText = 'Добавьте правильные ответы:';
    fields.appendChild(label);
    
    var qPairNum = 0
    for (let i = 1; i <= 17; i += 2) {
        var div = document.createElement('div');
        div.className = 'input-group w-75';
        fields.appendChild(div);
        
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
            input.id = 'q_right_answer_' + (i + j).toString();
            input.name = 'q_right_answer_' + (i + j).toString();
            div.appendChild(input);
        };
    };
};

function createFieldsForSpecialsQ() {
	for (i = 0, i <= 2, i++) {
		
	};
};

function createSpecialQ() {
	var fields = document.getElementById('fields');
	createTwoAnswers();
	
};

function createButtonSave() {
	
};

function createQTypeFields(selectValue) {
	if (window.editorInstance) {
		window.editorInstance.destroy();
	};
	if (window.editorInstanceTwo) {
		window.editorInstanceTwo.destroy();
	};
	if (window.editorInstanceThree) {
		window.editorInstanceThree.destroy();
	};
    removeFields();
    createDiffField();
    
	if (selectValue != specialQ) {
		var textArea = createTextArea('q_text', selectValue);
	};
	
    if (oneAnsQ.includes(selectValue)) {
        if (oneAnsQFiles.includes(selectValue)) {
			createFiles();
		};
		
		createOneAnswer();
	} else if (twoAnsQFiles.includes(selectValue)) {
		createFiles();
		createTwoAnswers();
	} else if (selectValue == manyAnsQ) {
		createManyAnswers();
	} else if (selectValue == manyAnsQFiles) {
		createFiles();
		createManyAnswers();
	} else if (selectValue == specialQ) {
		
	};
		
	
	//var script = document.createElement('script');
	//var ckeditor =  document.querySelector('[class="ck-body-wrapper"]');
	//console.log(ckeditor);
	//if (ckeditor) {
	//	ckeditor.remove();
	//};
	//script.type = 'module';
	//script.src = '/static/js/classic.editor.mjs';
	
	//document.getElementById('fields').appendChild(script);
	window.loadCKEditor(textArea);
};
