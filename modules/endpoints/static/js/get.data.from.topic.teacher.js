function createStructure(data) {
	var mainDiv = document.getElementById('forData');
	mainDiv.replaceChildren();
	
	const topic = data[0];
	
	switch (topic) {
		case 1:
			var table = createTableQuestionsCount(data[1]);
			mainDiv.appendChild(table[0]);
			mainDiv.appendChild(table[1]);
			break;
		case 2:
			let watchQuestions = createNavBarForTypes('getTypeQuestions');
			mainDiv.appendChild(watchQuestions);
			let questionsList = document.createElement('div');
			questionsList.setAttribute('id', 'questionsList');
			mainDiv.appendChild(questionsList);
			break;
		case 3:
			var createQuestions = createNavBarForTypes();
			//console.log(createQuestions);
			mainDiv.appendChild(createQuestions);
			var fields = document.createElement('div');
			fields.setAttribute('id', 'fields');
			mainDiv.appendChild(fields);
			break;
		case 4:
			let commonStatistics = createCommonStatisticsTable(data[1]);
			mainDiv.appendChild(commonStatistics);
			break;
		default:
			console.log('Something another');
	}
	
	
}

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
	}
	
	table.appendChild(tBody);
	
	return [topic, table]
}

// End for topic 1

// For topic 2 and 3

function createNavBarForTypes(func = 'createQTypeFields') {
	var problemTypes = [
		'1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
		'11', '12', '13', '14', '15', '16', '17', '18', '19-21',
		'22', '23', '24', '25', '26', '27'
	];
	
	var nav = document.createElement('div');
	nav.className = 'd-flex align-items-center mb-4';
	nav.setAttribute('style', 'max-width: 90vw; min-width: 300px');
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
		typeButton.setAttribute('onclick', `${func}('${type.slice(0, 2)}')`);
		var typeButtonLabel = document.createElement('label');
		typeButtonLabel.setAttribute('class', 'btn btn-outline-primary');
		typeButtonLabel.setAttribute('for', `r${type}`);
		typeButtonLabel.innerHTML = `${type}`;
		
		btnGroup.appendChild(typeButton);
		btnGroup.appendChild(typeButtonLabel);
	}
	overflow.appendChild(btnGroup);
	nav.appendChild(overflow);
	return nav;
}

// End for topic 2 and 3
// Start for topic 4

function createCommonStatisticsTable(commonStatistics) {
	let statisticsDiv = document.createElement('div');
	statisticsDiv.setAttribute('class', 'accordion');
	console.log(commonStatistics);
	const tableTitles = [
			'Тип задания',
			'Общее число решений',
			'Число правильных решение',
			'Точность попадания'
		]
	commonStatistics.forEach((student, index) => {
		const userDiv = document.createElement('div');
		userDiv.setAttribute('class', 'accordion-item');
		// const item = document.createElement('div');
		// item.setAttribute('class', 'accordion-item');
		let header = document.createElement('h2');
		header.setAttribute('class', 'accordion-header');
		const button = document.createElement('button');
		button.setAttribute('class', 'accordion-button collapsed');
		button.setAttribute('type', 'button');
		button.setAttribute('data-bs-toggle', 'collapse');
		button.setAttribute('data-bs-target', `#${index + 100}`);
		button.setAttribute('aria-expanded', 'false');
		button.setAttribute('aria-controls', `${index + 100}`);
		button.innerHTML = student[0];
		// header.innerHTML = student[0];
		header.appendChild(button);
		userDiv.appendChild(header);

		const table = document.createElement('table');
		table.setAttribute('class', 'table table-bordered w-75');
		const tHead = document.createElement('thead');
		const tBody = document.createElement('tbody');
		const headTr = document.createElement('tr');
		headTr.setAttribute('class', 'table-primary');
		tableTitles.forEach(title => {
			let tTh = document.createElement('th');
			tTh.setAttribute('scope', 'col');
			tTh.innerHTML = title;
			headTr.appendChild(tTh);
		})
		table.appendChild(tHead);
		tHead.appendChild(headTr);

		Object.entries(student[1]).forEach(qTypeStat => {
			const tTr = document.createElement('tr');
			let tTd = document.createElement('td');
			tTd.innerHTML = qTypeStat[0];
			tTr.appendChild(tTd);

			qTypeStat[1].forEach(item => {
				let tTd = document.createElement('td');
				tTd.innerHTML = Math.round(item * 100) / 100;
				tTr.appendChild(tTd);
			})
			tBody.appendChild(tTr);
		});
		table.appendChild(tBody);

		let insideBody = document.createElement('div');
		insideBody.setAttribute('class', 'accordion-body');
		let body = document.createElement('div');
		body.setAttribute('id', `${index + 100}`);
		body.setAttribute('class', 'accordion-collapse collapse');
		insideBody.appendChild(table);
		body.appendChild(insideBody);
		userDiv.appendChild(body);
		statisticsDiv.appendChild(userDiv);
	});
	return statisticsDiv;
}

// end for topic 4