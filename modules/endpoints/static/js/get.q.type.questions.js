function createSeparator(size = '10', color = 'blue') {
    let line = document.createElement('hr');
    line.setAttribute('size', size);
    line.setAttribute('color', color);
    line.setAttribute('class', 'mb-3');
    return line;
}

function getStandardQuestions(questionsList) {
    const container = document.getElementById('questionsList');
    container.replaceChildren();

    questionsList.forEach((question, index) => {
        let questionDiv = document.createElement('div');
        questionDiv.setAttribute('id', `${question.id}`);
        container.appendChild(questionDiv);

        let titleQuestion = document.createElement('p');
        titleQuestion.setAttribute('class', 'mb-3 h4');
        titleQuestion.innerHTML = `Вопрос ${index + 1} (сложность: ${question.q_difficulty})`;
        questionDiv.appendChild(titleQuestion);

        let qText = document.createElement('div');
        qText.setAttribute('class', 'ck-content');
        qText.innerHTML = question.q_text;
        questionDiv.appendChild(qText);

        if (question.q_files) {
            var fileContainer = document.createElement('div');
            let title = document.createElement('p');
            title.className = 'fw-bold';
            title.innerHTML = 'Файлы для вопроса:';
            fileContainer.appendChild(title);
            question.q_files.split('&').forEach(filePath => {
                let p = document.createElement('p');
                p.innerHTML = filePath;
                fileContainer.appendChild(p);
            });
            questionDiv.appendChild(fileContainer);
        }

        const answerDiv = document.createElement('div');
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
        questionDiv.appendChild(answerDiv);
        container.appendChild(questionDiv);
        let separator = document.createElement('hr');
        separator.setAttribute('size', '10');
        separator.setAttribute('color', 'blue');
        separator.setAttribute('class', 'mb-3');
        container.appendChild(separator);
    });
}

function getSpecialQuestions(questionsList) {
    const container = document.getElementById('questionsList');
    container.replaceChildren();

    let count = 1;
    for (let i = 0; i < questionsList.length; i += 3) {
        const questionBlock = document.createElement('div');
        let blockTitle = document.createElement('p');
        blockTitle.setAttribute('class', 'fw-bold h4 mb-3');
        blockTitle.innerHTML = `Блок № ${count} (сложность: ${questionsList[i + 2].q_difficulty})`;
        questionBlock.appendChild(blockTitle);

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
            questionBlock.appendChild(titles[index]);
            let qText = document.createElement('div');
            qText.setAttribute('class', 'ck-content');
            qText.innerHTML = questionsList[i + slider].q_text;
            questionBlock.appendChild(qText);
            let rightAnswersTitle = document.createElement('p');
            rightAnswersTitle.setAttribute('class', 'fw-bold mb-3');
            rightAnswersTitle.innerHTML = 'Правильные ответы';
            questionBlock.appendChild(rightAnswersTitle);
            let rightAnswers = document.createElement('p');
            if (questionsList[i + slider].q_right_answer.includes('&')) {
                let answers = questionsList[i + slider].q_right_answer.split('&');
                rightAnswers.innerHTML = `${answers[0]}     ${answers[1]}`;
            } else {
                rightAnswers.innerHTML = questionsList[i + slider].q_right_answer;
            }
            questionBlock.appendChild(rightAnswers);
            questionBlock.appendChild(createSeparator('5', 'black'));
        });
        container.appendChild(questionBlock);
        container.appendChild(createSeparator())
        count += 1;
    }
}

