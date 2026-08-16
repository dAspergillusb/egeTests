function createSeparator(qId, size = '10', color = 'blue') {
    let line = document.createElement('hr');
    line.setAttribute('name', `${qId}`);
    line.setAttribute('size', size);
    line.setAttribute('color', color);
    line.setAttribute('class', 'mb-3');
    return line;
}

function getStandardQuestions(questionsList, toCreate = true) {
    const container = document.getElementById('questionsList');
    if (toCreate) {
        container.replaceChildren();
    }

    questionsList.forEach((question, index) => {
        let contentDiv;
        if (toCreate) {
            let questionDiv = document.createElement('div');
            questionDiv.setAttribute('name', `${question.q_id}`);
            questionDiv.setAttribute('id', `${question.q_id}`);
            container.appendChild(questionDiv);

            let titleQuestion = document.createElement('p');
            titleQuestion.setAttribute('class', 'mb-3 h4');
            titleQuestion.innerHTML = `Вопрос ${index + 1} (сложность: ${question.q_difficulty})`;
            questionDiv.appendChild(titleQuestion);


            contentDiv = document.createElement('div');
            contentDiv.setAttribute('name', `content${question.q_id}`);
            questionDiv.appendChild(contentDiv);
        } else {
            contentDiv = document.querySelector(`div[name="content${question.q_id}"]`);
            contentDiv.replaceChildren();
            contentDiv.hidden = false;
        }

        let qText = document.createElement('div');
        // qText.setAttribute('name', `content${question.q_id}`);
        qText.setAttribute('class', 'ck-content');
        qText.innerHTML = question.q_text;
        contentDiv.appendChild(qText);

        if (question.q_files) {
            var fileContainer = document.createElement('div');
            // fileContainer.setAttribute('name', `content${question.q_id}` );
            let title = document.createElement('p');
            title.className = 'fw-bold';
            title.innerHTML = 'Файлы для вопроса:';
            fileContainer.appendChild(title);
            question.q_files.split('&').forEach(filePath => {
                let a = document.createElement('a');
                a.innerHTML = filePath.split("/").slice(-1);
                a.href = filePath;
                a.setAttribute('download', '')
                fileContainer.appendChild(a);
                fileContainer.appendChild(document.createElement('p'));
            });
            contentDiv.appendChild(fileContainer);
        }

        const answerDiv = document.createElement('div');
        // answerDiv.setAttribute('name', `content${question.q_id}`);
        let title = document.createElement('p');
        title.className = 'fw-bold';
        title.innerHTML = 'Правильные ответы:';
        answerDiv.appendChild(title);
        if (question.q_right_answer.includes('&')) {
            const answers = question.q_right_answer.split('&');
            for (let i = 0; i < answers.length; i += 2) {
                let p = document.createElement('p');
                p.innerHTML = `${answers[i]}    ${answers[i + 1]}`;
                answerDiv.appendChild(p);
            }
        } else {
            let p = document.createElement('p');
            p.innerHTML = question.q_right_answer;
            answerDiv.appendChild(p);
        }
        contentDiv.appendChild(answerDiv);
        if (toCreate) {
            container.appendChild(contentDiv);

            let buttonsGroup = createActionButtons(question.q_id);
            container.appendChild(buttonsGroup);

            // let separator = document.createElement('hr');
            // separator.setAttribute('name', `${question.q_id}`);
            // separator.setAttribute('size', '10');
            // separator.setAttribute('color', 'blue');
            // separator.setAttribute('class', 'mb-3');
            container.appendChild(createSeparator(question.q_id));
        }
    });
}

function getSpecialQuestions(questionsList, toCreate = true) {
    const container = document.getElementById('questionsList');
    if (toCreate) {
        container.replaceChildren();
    }

    let count = 1;
    for (let i = 0; i < questionsList.length; i += 3) {
        let contentDiv;
        let questionBlock
        if (toCreate) {
            questionBlock = document.createElement('div');
            questionBlock.setAttribute('name', `${questionsList[i + 2].q_id}`);
            questionBlock.setAttribute('id', `${questionsList[i + 2].q_id}`);

            let blockTitle = document.createElement('p');
            blockTitle.setAttribute('class', 'fw-bold h4 mb-3');
            blockTitle.innerHTML = `Блок № ${count} (сложность: ${questionsList[i + 2].q_difficulty})`;
            questionBlock.appendChild(blockTitle);

            contentDiv = document.createElement('div');
            contentDiv.setAttribute('name', `content${questionsList[i + 2].q_id}`);
            questionBlock.appendChild(contentDiv);
        } else {
            contentDiv = document.querySelector(`div[name="content${questionsList[i + 2].q_id}"]`);
            contentDiv.replaceChildren();
            contentDiv.hidden = false;
        }

        let qNineteen = document.createElement('p');
        let qTwenty = document.createElement('p');
        let qTwentyOne = document.createElement('p');
        qNineteen.setAttribute('class', 'fw-bold h3 mb-2');
        qNineteen.innerHTML = '19';
        qTwenty.setAttribute('class', 'fw-bold h3 mb-2');
        qTwenty.innerHTML = '20';
        qTwentyOne.setAttribute('class', 'fw-bold h3 mb-2');
        qTwentyOne.innerHTML = '21';

        let sliders = [2, 0, 1];
        const titles = [qNineteen, qTwenty, qTwentyOne];
        sliders.forEach((slider, index) => {
            contentDiv.appendChild(titles[index]);
            let qText = document.createElement('div');
            qText.setAttribute('class', 'ck-content');
            qText.innerHTML = questionsList[i + slider].q_text;
            contentDiv.appendChild(qText);
            let rightAnswersTitle = document.createElement('p');
            rightAnswersTitle.setAttribute('class', 'fw-bold mb-3');
            rightAnswersTitle.innerHTML = 'Правильные ответы';
            contentDiv.appendChild(rightAnswersTitle);
            let rightAnswers = document.createElement('p');
            if (questionsList[i + slider].q_right_answer.includes('&')) {
                let answers = questionsList[i + slider].q_right_answer.split('&');
                rightAnswers.innerHTML = `${answers[0]}     ${answers[1]}`;
            } else {
                rightAnswers.innerHTML = questionsList[i + slider].q_right_answer;
            }
            contentDiv.appendChild(rightAnswers);
            contentDiv.appendChild(createSeparator('5', 'black'));
        });
        if (toCreate) {
            container.appendChild(questionBlock);
            let buttonGroup = createActionButtons(questionsList[i + 2].q_id);
            container.appendChild(buttonGroup);
            container.appendChild(createSeparator(questionsList[i + 2].q_id));
        }
        count += 1;
    }
}

function createActionButtons(q_id) {
    let buttonsNames = ['Сохранить', 'Отменить', 'Удалить', 'Изменить'];
    let buttonsNameAttr = ['save', 'cancel', 'remove', 'edit'];
    let buttonsEnabled = [true, true, false, false]
    let buttonsIdNames = [`save${q_id}`, `cancel${q_id}`, `remove${q_id}`, `change${q_id}`];
    let functions = [
        `saveQuestion('${q_id}', save${q_id}, cancel${q_id})`,
        `cancelQuestion('${q_id}', save${q_id}, cancel${q_id})`,
        `removeQuestion('${q_id}')`,
        `changeQuestion('${q_id}', save${q_id}, cancel${q_id}, change${q_id})`
    ];
    let buttonsGroup = document.createElement('div');
    buttonsGroup.setAttribute('name', `${q_id}`);
    buttonsGroup.setAttribute('class', 'btn-group mb-3');
    buttonsGroup.setAttribute('role', 'group');
    buttonsNames.forEach((buttonText, index) => {
        let button = document.createElement('button');
        button.innerHTML = buttonText;
        button.disabled = buttonsEnabled[index];
        button.setAttribute('id', buttonsIdNames[index]);
        button.setAttribute('name', buttonsNameAttr[index]);
        button.setAttribute('class', 'btn btn-outline-primary');
        button.setAttribute('type', 'button');
        button.setAttribute('onclick', `${functions[index]}`);
        buttonsGroup.appendChild(button);
    });

    return buttonsGroup;
}

function createFieldsForChangeQuestion(question, buttonSaveId, buttonChangeId) {
    let qDiv = document.querySelector(`div[name="content${question.q_id}"]`);
    qDiv.hidden = true;
    let mainDiv = document.querySelector(`div[name="${question.q_id}"]`);
    let fieldsDiv = document.createElement('div');
    fieldsDiv.setAttribute('id', 'fields');
    mainDiv.appendChild(fieldsDiv);
    createQTypeFields(
        `${question.q_number}`,
        question.q_difficulty,
        question.q_text,
        false,
        question.q_right_answer
    );

}

function cancelQuestion(qId, buttonSave, buttonCancel) {
    let fields = document.getElementById('fields');
    let contentDiv = document.querySelector(`div[name="content${qId}"`);
    let buttonsRemove = document.querySelectorAll('button[name="remove"]');
    let buttonsEdit = document.querySelectorAll('button[name="edit"]');
    fields.remove();
    contentDiv.hidden = false;
    buttonSave.disabled = true;
    buttonCancel.disabled = true;
    [...buttonsRemove, ...buttonsEdit].forEach(button => {
        button.disabled = false;
    })
}