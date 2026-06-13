function createStructure(data) {
	var mainDiv = document.getElementById('forData');
	mainDiv.replaceChildren();
	
	var topic = data[0];
	var countData = data[1];
	
	switch (topic) {
		case 1:
			var table = createTableQuestionsCount(countData);
			mainDiv.appendChild(table[0]);
			mainDiv.appendChild(table[1]);
			break;
		case 3:
			var createQuestions = createNavBarForTypes();
			//console.log(createQuestions);
			mainDiv.appendChild(createQuestions);
			var fields = document.createElement('div');
			fields.setAttribute('id', 'fields');
			mainDiv.appendChild(fields);
		default:
			console.log('Something another');
	};
	
	
};

// For topic 1

function createTableQuestionsCount(data) {
	var tableTopics = [
		'Тип задания',
		'Количество заданий',
		'Сложность "база"',
		'Сложность "средний"',
		'Сложность "сложный"'
	];
	var topic = document.createElement('h1');
	var table = document.createElement('table');
	var tHead = document.createElement('thead');
	var tBody = document.createElement('tbody');
	var tTr = document.createElement('tr');
	
	topic.className = 'h3 mb-4 fw-normal';
	topic.innerHTML = 'Количество заданий в базе данных:'
	
	table.className = 'table table-bordered w-75';
	
	tTr.className = 'table-primary';
	
	for (i = 0; i < 5; i++) {
		var tTh = document.createElement('th');
		tTh.setAttribute('scope', 'col');
		tTh.innerHTML = tableTopics[i];
		tTr.appendChild(tTh);
	};
	
	table.appendChild(tHead);
	tHead.appendChild(tTr);
	
	var types = new Map(Object.entries(data));
	for (type of types) {
		var tTr = document.createElement('tr');
		var tTd = document.createElement('td');
		tTd.innerHTML = type.at(0);
		tTr.appendChild(tTd);
		
		var items = new Map(Object.entries(type.at(1)));
		items.forEach(item => {
			var tTd = document.createElement('td');
			tTd.innerHTML = item;
			tTr.appendChild(tTd);
		});
		
		tBody.appendChild(tTr);
	};
	
	table.appendChild(tBody);
	
	return [topic, table]
};

// End for topic 1
// For topic 2

// End for topic 2
// For topic 3

function createNavBarForTypes() {
	var problemTypes = [
		'1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
		'11', '12', '13', '14', '15', '16', '17', '18', '19-21',
		'22', '23', '24', '25', '26', '27'
	];
	
	var nav = document.createElement('div');
	nav.className = 'd-flex align-items-center mb-4';
	nav.setAttribute('style', 'max-width: 90vw; min-width=300px');
	var overflow = document.createElement('div');
	overflow.ClassName = 'overflow-auto';
	overflow.setAttribute('style', 'max-width: 90vw;');
	var btnGroup = document.createElement('div');
	btnGroup.className = 'btn-group bg-light';
	btnGroup.setAttribute('role', 'group');
	btnGroup.setAttribute('aria-label', 'Типы заданий');
	for (type of problemTypes) {
		var typeButton = document.createElement('input');
		typeButton.setAttribute('type', 'radio');
		typeButton.setAttribute('class', 'btn-check');
		typeButton.setAttribute('name', 'typeButton');
		typeButton.setAttribute('autocomplete', 'off');
		typeButton.setAttribute('id', `r${type}`);
		typeButton.setAttribute('onclick', `createQTypeFields('${type}')`);
		var typeButtonLabel = document.createElement('label');
		typeButtonLabel.setAttribute('class', 'btn btn-outline-primary');
		typeButtonLabel.setAttribute('for', `r${type}`);
		typeButtonLabel.innerHTML = `${type}`;
		
		btnGroup.appendChild(typeButton);
		btnGroup.appendChild(typeButtonLabel);
	};
	overflow.appendChild(btnGroup);
	nav.appendChild(overflow);
	return nav;
};

// End for topic 3
