// main eventListener for navButtons
let navButtonDiv = document.getElementById('navButtons');
let navButtons = document.querySelectorAll('button[name="navButton"]');
setTimeout(() => {
    document.querySelector('div[id="instruction"]').classList.add('show');
}, 100);
navButtonDiv.addEventListener('click', async (event) => {
  let button = event.target.closest('button[name="navButton"]');
  if (!button || button.className.includes('btn-primary')) return;
  let dbButtons = document.querySelectorAll('button[name="navDBButton"]');
  if (dbButtons) {
      navButtonDiv.removeEventListener('click', handlerDBWorking);
      dbButtons.forEach((button) => {
          button.remove();
      })
  }
  navButtons.forEach((element) => {
      element.className = 'btn btn-outline-primary';
  });
  let forData = document.getElementById('forData');
  forData.removeEventListener('click', handlerTestSessionDelete);
  await showInstruction(false);
  // document.querySelector('div[id="instruction"]').hidden = true;
  button.className = 'btn btn-primary';
  let buttonID = button.dataset.id;
  if (buttonID === '0') {
      // document.querySelector('div[id="instruction"]').hidden = false;
      document.querySelector('div[id="forData"]').replaceChildren();
      await showInstruction();
  } else if (buttonID === '1') {
      forData.replaceChildren();
      let awaitingCard = `
      <h1 class="fw-bold h2 fade">Список пользователей:</h1>
      <div class="card mb-2 overflow-x-auto fade">
        <div class="card-body">
            <div class="card-title">
                <h5 class="card-title placeholder-glow">
                    <span class="placeholder col-3"></span>
                    <span class="placeholder col-3"></span>
                    <span class="placeholder col-3"></span>
                </h5>
            </div>
            <div class="row align-items-center">
                <div class="col">
                    <p class="card-text placeholder-glow">Права: <span class="placeholder col-6"></span></p>
                </div>
                <div class="col">
                    <p class="card-text placeholder-glow">Класс: <span class="placeholder col-6"></span></p>
                </div>
                <div class="col">
                    <p class="card-text placeholder-glow">Пол: <span class="placeholder col-6"></span></p>
                </div>
                <div class="col">
                    <p class="card-text placeholder-glow">Состояние: <span class="placeholder col-6"></span></p>
                </div>
                <div class="col">
                    <div class="btn-group-vertical" role="group">
                        <a class="btn btn-outline-primary disabled placeholder-glow col-6">Изменить</a>
                        <a class="btn btn-outline-primary disabled placeholder-glow col-6">Удалить</a>
                    </div>
                </div>
            </div>    
        </div>
      </div>
      `;
      forData.insertAdjacentHTML('beforeend', awaitingCard);
      for (let item of Array.from(forData.children)) {
          await sleep(100);
          item.classList.add('show');
      }
      await getAllUsers();
  } else if (buttonID === '2') {
      await constructMassiveUsersWorking();
  } else if (buttonID === '3') {
      await constructDBWorking();
  }
});

// const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// functions for users administration
async function getAllUsers() {
  try {
    const response = await fetch('/users', {
      method: 'get',
      headers: {'Content-Type': 'application/json'},
    });
    if (response.ok) {
      const result = await response.json();
      await createUsersCards(result);
    }
  }  catch (error) {
    console.log(error);
  }
}

async function showInstruction(show = true) {
    let instruction = document.getElementById('instruction');
    if (!show && instruction.hidden) {
        return;
    }
    // await sleep(100);
    if (show) {
        instruction.hidden = false;
        await sleep(100);
        instruction.classList.add('show');
    } else {
        instruction.classList.remove('show');
        await sleep(100);
        instruction.hidden = true;
    }
}

async function createUsersCards(users, forCreate = true, theNextDiv = null) {
    let forData = document.querySelector('div[id="forData"]');
    if (forCreate) {
        forData.replaceChildren();
        forData.removeEventListener('click', handleMassiveDBButtonsEvents);
        let text = `<h1 class="fw-bold h2 fade">Список пользователей:</h1>`;
        forData.insertAdjacentHTML('beforeend', text);
    }
    // console.log(users);
    let roles = {
        "student": "Ученик",
        "teacher": "Учитель",
        "admin": "Администратор"
    };
    users.forEach(user => {
        const userCard = `
        <div class="card mb-2 overflow-x-auto fade" id="${user.user_id}">
            <form id="form-${user.user_id}" enctype="multipart/form-data">
                <div class="card-body fade show" id="card-body-${user.user_id}">
                    <h5 class="card-title">${user.firstname} ${user.lastname} (${user.username})</h5>
                    <div class="row align-items-center">
                        <div class="col">
                            <p class="card-text">Права: ${roles[user.rank]}</p>
                        </div>
                        ${user.rank === 'student' ?
                        `<div class="col">
                            <p class="card-text">Класс: ${user.school_class}</p>
                        </div>` : ''}
                        <div class="col">
                            <p class="card-text">Пол: ${user.sex}</p>
                        </div>
                        <div class="col">
                            <p class="card-text">Состояние: <a style="color: ${user.active ? 'green' : 'tomato'}">${user.active ? 'Активен' : 'Заблокирован'}</a></p>
                        </div>
                        <div class="col-2 align-content-end">
                            <div class="btn-group-vertical" role="group">
                                <button class="btn btn-outline-primary" type="button" name="change" data-id="${user.user_id}">Изменить</button>
                                <button class="btn btn-outline-primary" type="button" name="delete" data-id="${user.user_id}">Удалить</button>
                            </div>
                        </div>
                    </div>                    
                </div>
            </form>
        </div>
        `;
        if (theNextDiv) {
            theNextDiv.insertAdjacentHTML('beforebegin', userCard);
        } else {
            forData.insertAdjacentHTML('beforeend', userCard);
        }
    });
    if (forCreate) {
        let newUserButton = `
        <button class="btn btn-outline-primary mb-3 mt-3 fade" type="button" data-id="create-user">Создать пользователя</button>
        `;
        forData.insertAdjacentHTML('beforeend', newUserButton);
        document.querySelector('button[data-id=create-user]').addEventListener('click', async () => {
            await createNewUserCard();
        });
        forData.addEventListener('click', handleButtonsEvents);
        for (let item of Array.from(forData.children)) {
           await sleep(50);
           item.classList.add('show');
        }
    } else {
        document.querySelector('button[data-id="create-user"]').disabled = false;
        await sleep(100);
        forData.querySelector(`div[id="${users[0].user_id}"]`).classList.add('show');
    }

}

async function handleButtonsEvents(event) {
    const changeEvent = event.target.closest('button[name="change"]');
    const saveEvent = event.target.closest('button[name="save"]');
    const cancelEvent = event.target.closest('button[name="cancel"]');
    const deleteEvent = event.target.closest('button[name="delete"]');
    let action = changeEvent || saveEvent || cancelEvent || deleteEvent || null;
    if (!action) {
        return;
    }
    let actionId = action.dataset.id;
    if (changeEvent) {
        let user = await getUser(actionId);
        await changeUser(user);
    }
    if (saveEvent) {
        await changeUserData(actionId);
    }
    if (cancelEvent) {
        document.querySelector(`div[id="card-body-change-${actionId}"]`).remove();
        let cardBoby = document.querySelector(`div[id="card-body-${actionId}"]`);
        cardBoby.hidden = false;
        await sleep(100);
        cardBoby.classList.add('show');
    }
    if (deleteEvent) {
        await deleteUser(deleteEvent.dataset.id);
    }
}

async function changeUser(user) {
    let form = document.querySelector(`form[id="form-${user.user_id}"]`);
    let cardData = document.querySelector(`div[id="card-body-${user.user_id}"]`);
    cardData.classList.remove('show');
    await sleep(100);
    cardData.hidden = true;

    let roles = ['student', 'teacher', 'admin'];
    let sexes = ['муж', 'жен'];
    let formChangeUser = `
    <div class="card-body overflow-x-auto fade" id="card-body-change-${user.user_id}">
        <div class="card-title">
            <div class="input-group w-75 mt-3">
                <span class="input-group-text fw-bold">Имя и фамилия</span>
                <input class="form-control" type="text" aria-label="Имя" name="firstname" value="${user.firstname}">
                <input class="form-control" type="text" aria-label="Фамилия" name="lastname" value="${user.lastname}">
            </div>
        </div>
        <div class="row mt-3 align-items-center">
            <div class="col-3">
                <div class="input-group">
                    <label class="input-group-text" for="roles">Права</label>
                    <select class="form-select" id="roles-${user.user_id}" name="rank">
                        <option id="student" value="student">Ученик</option>
                        <option id="teacher" value="teacher">Учитель</option>
                        <option id="admin" value="admin">Администратор</option>
                    </select>
                </div>
            </div>
            <div class="col">
                <div class="input-group" ${user.rank === 'student' ? '' : 'hidden'}>
                    <span class="input-group-text">Класс</span>
                    <input class="form-control" type="text" aria-label="Класс" name="school_class" value="${user.school_class}">
                </div>
            </div>
            <div class="col">
                <div class="input-group">
                    <label class="input-group-text" for="roles">Пол</label>
                    <select class="form-select" id="sex-${user.user_id}" name="sex">
                        <option id="муж" value="муж">Муж</option>
                        <option id="жен" value="жен">Жен</option>
                    </select>
                </div>
            </div>
            <div class="col-3">
                <div class="input-group">
                    <span class="input-group-text">Новый пароль</span>
                    <input class="form-control" type="text" aria-label="Пароль" name="password">
                </div>
            </div>
            <div class="col">
                <div class="form-check form-switch">
                    <label class="form-check-label" for="switch-${user.user_id}">Активность </label>
                    <input class="form-check-input" type="checkbox" role="switch" id="switch-${user.user_id}" aria-label="Активность" name="active">
                </div>
            </div>
            <div class="col-2">
                <div class="btn-group-vertical" role="group">
                    <button type="button" class="btn btn-outline-primary" name="save" data-id="${user.user_id}">Сохранить</button>
                    <button type="button" class="btn btn-outline-primary" name="cancel" data-id="${user.user_id}">Отменить</button>
                </div>
            </div>
        </div>
    </div>
    `;
    form.insertAdjacentHTML('beforeend', formChangeUser);
    form.querySelector(`select[id=roles-${user.user_id}]`).selectedIndex = roles.indexOf(user.rank);
    form.querySelector(`select[id=sex-${user.user_id}]`).selectedIndex = sexes.indexOf(user.sex);
    if (user.active) {
        document.querySelector(`input[id="switch-${user.user_id}"]`).checked = true;
    }
    await sleep(100);
    form.querySelector(`div[id="card-body-change-${user.user_id}"]`).classList.add('show');
}

async function createUserCard(nextUserId) {
    let forData = document.querySelector('div[id="forData"]');
    let formChangeUser = `
    <div class="card mb-2 overflow-x-auto fade" id="${nextUserId}">
        <form id="form-${nextUserId}" enctype="multipart/form-data">
            <div class="card-body" id="card-body-create-${nextUserId}">
                <div class="card-title">
                    <div class="input-group w-75 mt-3">
                        <span class="input-group-text fw-bold">Имя, фамилия, имя пользователя</span>
                        <input class="form-control" type="text" aria-label="Имя" name="firstname">
                        <input class="form-control" type="text" aria-label="Фамилия" name="lastname">
                        <input class="form-control" type="text" aria-label="Имя пользователя" name="username">
                    </div>
                </div>
                <div class="row mt-3 align-items-center">
                    <div class="col-3">
                        <div class="input-group">
                            <label class="input-group-text" for="roles">Права:</label>
                            <select class="form-select" id="roles-${nextUserId}" name="rank">
                                <option id="student" value="student" selected>Ученик</option>
                                <option id="teacher" value="teacher">Учитель</option>
                                <option id="admin" value="admin">Администратор</option>
                            </select>
                        </div>
                    </div>
                    <div class="col">
                        <div class="input-group" id="schoolClass-${nextUserId}">
                            <span class="input-group-text">Класс</span>
                            <input class="form-control" type="text" aria-label="Класс" name="school_class">
                        </div>
                    </div>
                    <div class="col">
                        <div class="input-group">
                            <label class="input-group-text" for="roles">Пол</label>
                            <select class="form-select" id="sex-${nextUserId}" name="sex">
                                <option selected>Пол...</option>
                                <option id="муж" value="муж">Муж</option>
                                <option id="жен" value="жен">Жен</option>
                            </select>
                        </div>
                    </div>  
                    <div class="col-3">
                        <div class="input-group">
                            <span class="input-group-text">Новый пароль</span>
                            <input class="form-control" type="text" aria-label="Пароль" name="password">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-check form-switch">
                            <label class="form-check-label" for="switch-${nextUserId}">Активность </label>
                            <input checked class="form-check-input" type="checkbox" role="switch" id="switch-${nextUserId}" aria-label="Активность" name="active">
                        </div>
                    </div>
                    <div class="col">
                        <div class="btn-group-vertical" role="group">
                            <button type="button" class="btn btn-outline-primary" id="save-${nextUserId}">Сохранить</button>
                            <button type="button" class="btn btn-outline-primary" id="cancel-${nextUserId}">Отменить</button>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
    `;
    forData.querySelector('button[data-id="create-user"]').insertAdjacentHTML('beforebegin', formChangeUser);
    forData.querySelector(`button[id=cancel-${nextUserId}]`).addEventListener('click', async () => {
        let card = forData.querySelector(`div[id="${nextUserId}"]`)
        card.classList.remove('show');
        await sleep(300);
        card.remove();
        let createButton = forData.querySelector('button[data-id="create-user"]');
        createButton.innerHTML = 'Создать пользователя';
        createButton.disabled = false;
    });
    forData.querySelector(`select[id="roles-${nextUserId}"]`).addEventListener('change', (event) => {
        let schoolClass = forData.querySelector(`div[id="schoolClass-${nextUserId}"]`);
        event.target.value === 'student' ? schoolClass.hidden = false : schoolClass.hidden = true;
    });
    forData.querySelector(`button[id=save-${nextUserId}]`).addEventListener('click', async () => {
        await createUser(nextUserId);
    });
    await sleep(100);
    forData.querySelector(`div[id="${nextUserId}"]`).classList.add('show');
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth',
    });
}

function getTheNextDiv(divId) {
    let forDataArray = [...document.querySelector('div[id="forData"]').children];
    let indexDiv = forDataArray.indexOf(document.querySelector(`div[id="${divId}"]`));
    return forDataArray[indexDiv + 1];
}

async function getUser(userId) {
    try {
        const response = await fetch(`/users/${userId}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.log(error);
    }
}

async function getNextId() {
    try {
        const response = await fetch(`/users`, {
            method: 'get',
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            const result = await response.json();
            return Math.max(...result.map(user => user.user_id)) + 1;
        }
    } catch (error) {
        console.error(error);
    }
}

async function createNewUserCard() {
    let createButton = document.querySelector('button[data-id=create-user]')
    createButton.innerHTML = `
        <div class="spinner-border spinner-border-sm text-primary ps-2" role="status"></div>
        <label>Ожидаю...</label>
    `;
    createButton.disabled = true;
    let nextId = await getNextId();
    await createUserCard(nextId);
}

async function createUser(nextId) {
    let form = document.querySelector(`form[id="form-${nextId}"]`);
    const formData = new FormData(form);
    // console.log(Object.fromEntries(formData));
    let check = document.querySelector(`input[id="switch-${nextId}"]`);
    formData['active'] = check.checked;
    try {
        const response = await fetch('/users', {
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(Object.fromEntries(formData))
        });
        if (response.ok) {
            const result = await response.json();
            let messages = ["Пользователь успешно создан!", "В форме есть ошибки или имя пользователя существует!"];
            if (result) {
                let insertPlace = document.querySelector(`div[id="${nextId}"]`);
                await createUsersCards([result], false, insertPlace);
                await sleep(100);
                insertPlace.remove();
                let createButton = document.querySelector('button[data-id="create-user"]');
                createButton.innerHTML = 'Создать пользователя';
                createAlert(result, messages);
            } else {
                createAlert(result, messages);
            }
        }
    } catch (error) {
        console.error(error);
    }
}

async function changeUserData(userId) {
    let form = document.querySelector(`form[id=form-${userId}]`);
    let formData = new FormData(form);
    let check = form.querySelector(`input[id="switch-${userId}"]`);
    formData = Object.fromEntries(formData);
    formData['active'] = check.checked;
    try {
        const response = await fetch(`/users/${userId}`, {
           method: 'PATCH',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify(formData)
        });
        if (response.ok) {
            const result = await response.json();
            let messages = ["Данные успешно изменены!", "Проверьте правильность заполнения формы!"];
            if (result) {
                console.log(result);
                let theNextDiv = getTheNextDiv(userId);
                await createUsersCards([await getUser(userId)], false, theNextDiv);
                document.querySelector(`div[id="${userId}"]`).remove();
                createAlert(result, messages);
            } else {
                createAlert(result, messages);
            }
        }
    } catch (error) {
        console.error(error);
    }
}

async function deleteUser(userId) {
    let card = document.querySelector(`div[id="${userId}"]`);
    try {
        const response = await fetch(`/users/${userId}`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            const result = await response.json();
            let messages = ["Пользователь успешно удалён!", "Пользователь не существует! Проверьте базу данных."];
            if (result) {
                card.classList.remove('show');
                await sleep(400);
                card.remove();
                createAlert(result, messages);
            } else if (result === 404) {
                createAlert(result, messages);
            } else if (result === 403) {
                createAlert(false, ['', 'Похоже вы удаляете последнего администратора...<br>Без администратора системой нельзя управлять!'])
            } else {
                createAlert(result, ['', 'Похоже, что у пользователя есть активная сессия.<br>Нельзя удалять пользователя с активными сессиями!']);
            }

        }
    } catch (error) {
        console.error(error);
    }
}
// functions for massive working with users
async function getDatabaseNames() {
    try {
        const response = await fetch('/databases', {
            method: "GET",
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error(error);
    }
}

async function constructMassiveUsersWorking() {
    let dbNames = await getDatabaseNames();
    let usersDbName = dbNames.USERS_DB_NAME;
    let usersStatisticsDbName = dbNames.USERS_STATISTICS_DB_NAME;
    let dailyStatisticsDbName = dbNames.DAILY_STATISTICS_DB_NAME;
    let forData = document.querySelector('div[id="forData"]');
    forData.replaceChildren();
    forData.removeEventListener('click', handleButtonsEvents);

    let importCsvFile = `
    <div class="fade" id="massiveUsersWorking">
    <div class="card overflow-x-auto">
        <div class="card-header">
            <h3 class="card-title fw-semibold">
                Массовое добавление пользователей
            </h3>
        </div>
        <div class="card-body">
            <form id="dbData">
                <label class="mb-2 h4">Имя базы данных пользователей</label>
                <input class="form-control mb-3 w-75" type="text" name="users_db_name" id="users_db_name" value="${usersDbName}" disabled>
                <label class="mb-2 h4">Имя базы данных статистики пользователей</label>
                <input class="form-control mb-3 w-75" type="text" name="users_statistics_db_name" id="users_statistics_db_name" value="${usersStatisticsDbName}" disabled>
                <label class="mb-2 h4">Имя базы данных истории прохождения тестов</label>
                <input class="form-control mb-3 w-75" type="text" name="daily_statistics_db_name" id="daily_statistics_db_name" value="${dailyStatisticsDbName}" disabled>
                <label class="mb-2 h4">Добавьте csv-файл, на основе которого будут изменения</label>
                <input
                    type="file"
                    class="form-control mb-3 ms-4 mt-3 w-75"
                    id="csv_file"
                    name="csv_file"
                    aria-describedby="inputGroupFileAddon04"
                    aria-label="Upload"
                >
            </form>
        </div>
        <div class="card-footer">
            <div class="container-fluid">
                <button class="btn btn-outline-primary pe-2" type="button" id="rewriteDBsButton" data-bs-toggle="modal" data-bs-target="#confirm">Перезаписать базы</button>
                <button class="btn btn-outline-primary pe-2" type="button" data-id="addToDBs">Добавить к существующим</button>
            </div>
        </div>
        <div class="modal fade" id="confirm" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false" aria-labelledby="confirmLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5" id="confirmLabel">Вы уверены?</h1>
                    </div>
                    <div class="modal-body">
                        При перезаписи баз данных не забудьте добавить строку для администратора в csv-файле.
                        Если этого не сделать, вы потеряете всякий доступ к управлению системой!
                        Вы уверены, что хотите перезаписать базы пользователей?
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Нет</button>
                        <button type="button" class="btn btn-outline-primary" data-id="rewriteDBs" data-bs-dismiss="modal">Да</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>
    `;
    forData.insertAdjacentHTML('beforeend', importCsvFile);
    forData.addEventListener('click', handleMassiveDBButtonsEvents);
    await sleep(150);
    forData.querySelector('div[id="massiveUsersWorking"]').classList.add('show');
}

async function handleMassiveDBButtonsEvents(event) {
    let rewrite = event.target.closest('button[data-id="rewriteDBs"]');
    let add = event.target.closest('button[data-id="addToDBs"]');
    let forData = document.getElementById('forData');
    if (!rewrite && !add) {
        return;
    }
    if (!forData.querySelector('input[name="csv_file"]').files[0]) {
            createAlert(false, ['', 'Необходимо добавить файл с данными пользователей!'])
            return;
    }
    if (rewrite) {
        let rewriteButton = document.getElementById('rewriteDBsButton');
        rewriteButton.innerHTML = `
        <div class="spinner-border spinner-border-sm text-primary ps-2" role="status"></div>
        <label>Стираю и перезаписываю...</label>
        `;
        rewriteButton.disabled = true;
        await addToCreateRewriteUsers('rewrite', rewriteButton, 'Перезаписать базы');
    } else if (add) {
        add.innerHTML = `
        <div class="spinner-border spinner-border-sm text-primary ps-2" role="status"></div>
        <label>Добавляю...</label>
        `;
        add.disabled = true;
        await addToCreateRewriteUsers('add', add, 'Добавить к существующим');
    }
}

async function addToCreateRewriteUsers(action, button, buttonText) {
    let data = document.querySelector('form[id="dbData"]');
    let form = new FormData(data);
    try {
        const response = await fetch(`/databases/table/${action}`, {
            method: 'POST',
            body: form
        });
        if (response.ok) {
            const result = await response.json();
            if (result.status === 204) {
                createAlert(result, [result.message, '']);
            } else if (result.status === 409) {
                createAlert(!result, ['', result.message]);
            }
        }
    } catch (error) {
        console.error(error);
    }
    button.innerHTML = buttonText;
    button.disabled = false;
}

// functions for database administration
async function constructDBWorking() {
    let forData = document.querySelector('div[id="forData"]');
    forData.removeEventListener('click', handlerSessionsDeletion);
    forData.replaceChildren();
    let buttonsExist = document.querySelector('button[data-id="4"]');
    if (!buttonsExist) {
        let navButtons = document.getElementById('navButtons');
        let newButtons = `
        <button data-id="4" name="navDBButton" class="btn btn-outline-primary fade d-none">Активные сессии пользователей</button>
        <button data-id="5" name="navDBButton" class="btn btn-outline-primary fade d-none">Активные сессии тестов</button>
        <button data-id="6" name="navDBButton" class="btn btn-outline-primary fade d-none">Очистка/добавление баз данных</button>
        <button data-id="7" name="navDBButton" class="btn btn-outline-primary fade d-none">Выбор базы данных</button>
        `;
        navButtons.insertAdjacentHTML('beforeend', newButtons);
        navButtons.addEventListener('click', handlerDBWorking);
        let navDBButtons = navButtons.querySelectorAll('button[name="navDBButton"]');
        for (let button of navDBButtons) {
            button.classList.remove('d-none');
            await sleep(50);
            button.classList.add('show');
        }
        for (let button of navDBButtons) {
            await sleep(50);
            button.className = 'btn btn-outline-primary';
        }
    }
}

async function handlerDBWorking(event) {
    let clickedButton = event.target.closest('button[name="navDBButton"]');
    if (!clickedButton || clickedButton.className.includes('btn-primary')) return;
    let navDBButtons = document.querySelectorAll('button[name="navDBButton"]');
    navDBButtons.forEach((element) => {
      element.className = 'btn btn-outline-primary';
    });
    let forData = document.getElementById('forData')
    forData.removeEventListener('click', handlerTestSessionDelete);
    forData.replaceChildren();
    let buttonId = clickedButton.dataset.id;
    clickedButton.className = 'btn btn-primary';
    if (buttonId === "4") {
        await getActiveUsersSessions();
    } else if (buttonId === "5") {
        await getActiveStudentsTestSessions();
    } else if (buttonId === "6") {
        await getDBsForClearStructure();
    } else if (buttonId === "7") {
        await getActiveDatabaseList();
    }
}

async function getActiveUsersSessions() {
    try {
        const response = await fetch(`/databases/active_users_sessions`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            let forData = document.querySelector('div[id="forData"]');
            let placeholder = `
              <h1 class="fw-bold h2 fade">Список сессий:</h1>
              <div class="card mb-2 overflow-x-auto fade" id="placeholder">
                <div class="card-body">
                    <div class="card-title">
                        <h5 class="card-title placeholder-glow">
                            <span class="placeholder col-3"></span>
                            <span class="placeholder col-3"></span>
                            <span class="placeholder col-3"></span>
                        </h5>
                    </div>
                    <div class="row align-items-center">
                        <div class="col">
                            <p class="card-text placeholder-glow">Id сессии: <span class="placeholder col-6"></span></p>
                        </div>
                        <div class="col">
                            <p class="card-text placeholder-glow">Устройство/браузер: <span class="placeholder col-6"></span></p>
                        </div>
                        <div class="col">
                            <p class="card-text placeholder-glow">IP-адресс: <span class="placeholder col-6"></span></p>
                        </div>
                        <div class="col">
                            <p class="card-text placeholder-glow">Дата сессии: <span class="placeholder col-6"></span></p>
                        </div>
                        <div class="col">
                            <div class="btn-group-vertical" role="group">
                                <a class="btn btn-outline-primary disabled placeholder-glow col-6">Удалить</a>
                            </div>
                        </div>
                    </div>    
                </div>
              </div>
              `;
            forData.replaceChildren();
            forData.insertAdjacentHTML('beforeend', placeholder);
            for (let item of Array.from(forData.children)) {
                await sleep(100);
                item.classList.add('show')
            }
            const result = await response.json();
            await createActiveSessionsCards(Array.from(result));
        }
    } catch (error) {
        console.error(error);
    }
}

async function createActiveSessionsCards(sessions) {
    document.getElementById('placeholder').remove();
    let forData = document.querySelector('div[id="forData"]');
    // console.log(sessions);
    let expired = [];
    sessions.forEach((session) => {
        if (session.expired) expired.push(session.user_id);
        let sessionCard = `
          <div class="card mb-2 overflow-x-auto fade" id="${session.user_id}">
            <div class="card-body">
                <div class="card-title">
                    <h5 class="card-title">
                        ${session.is_current_session ? '<button class="btn btn-outline-success" style="color: #20c997;">Текущая сессия</button>' : ''}
                    </h5>
                    <h5 class="card-title">
                        Сессия: ${session.firstname} ${session.lastname} (${session.username})
                    </h5>
                </div>
                <div class="row align-items-center">
                    <div class="col-10">
                        <p class="card-text"><b>Id сессии:</b> ${session.session_id}</p>
                        <p class="card-text"><b>Устройство/браузер:</b> ${session.user_agent}</p>
                        <p class="card-text"><b>IP-адресс:</b> ${session.ip_address}</p>
                        <p class="card-text">${session.expired ? '<b style="color: tomato;">Сессия истекла</b>' : '<b style="color: #20c997;">Сессия истекает</b>'}: ${session.expire_date}</p>
                    </div>
                    <div class="col-2">
                        <div class="btn-group-vertical" role="group">
                            ${session.expired ? `<button class="btn btn-outline-primary" id="${session.user_id}" data-id="${session.session_id}" name="sessionDelete" type="button">Удалить</button>` : '<a class="btn btn-outline-primary disabled">Удалить</a>'}
                        </div>
                    </div>
                </div>    
            </div>
          </div>
        `;
        forData.insertAdjacentHTML('beforeend', sessionCard);
    });
    forData.addEventListener('click', handlerSessionsDeletion);
    for (let item of Array.from(forData.children).slice(1,)) {
        await sleep(50);
        item.classList.add('show');
    }
}

async function handlerSessionsDeletion(event) {
    let clickedButton = event.target.closest('button[name="sessionDelete"]');
    if (!clickedButton) return;
    clickedButton.innerHTML = `
    <div class="spinner-border spinner-border-sm text-primary ps-2" role="status"></div>
    <label>Удаляю...</label>
    `;
    let sessionId = clickedButton.dataset.id;
    let cardId = clickedButton.id;
    await deleteSession(sessionId);
    let cardForDelete = document.getElementById(cardId);
    cardForDelete.classList.remove('show');
    await sleep(200);
    cardForDelete.remove();
}

async function deleteSession(sessionId) {
    try {
        const response = await fetch(`/database/active_users_sessions/${sessionId}`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok && response.status === 200) {
            createAlert(true, ['Старая сессия успешно удалена', '']);
        } else {
            createAlert(false, ['', 'Во время удаления возникли ошибки. Попробуйте позже.'])
        }
    } catch (error) {
        console.error(error);
    }
}

async function getDBsForClearStructure() {
    let forData = document.querySelector('div[id="forData"]');
    let clearStructure = `
    <h5 class="fw-semibold mb-5 fade">
        <p><b style="color: tomato"><u>Перед действиями прочитайте внимательно!</u></b></p>
        <p>&emsp;Работа с базами данных может привести к непредсказуемым последствиям, в том числе <u style="color: #aa0000;">полной потери доступа к системе</u>!
        Убедитесь в том, что вы точно знаете что делаете. Также работа с базой данных пользователей (очистка или создание)
        должна производиться только тогда, когда вы точно уверены в том, что <u style="color: #aa0000;">ваша сессия единственна</u>
        и больше нет одновременно подключенных учеников, учителей или администраторов!</p>
    </h5>
    <div class="card overflow-x-auto fade">
        <div class="card-header">
            <h3 class="card-title fw-semibold">
                Очистка баз данных
            </h3>
        </div>
        <div class="card-body">
            <form id="dbData">
                <div class="card-text fw-bold mb-2">Выберите тип базы данных:</div>
                <select class="form-select mb-4" id="dbType" aria-label="Тип базы данных">
                  <option value="" selected>...</option>
                  <option name="users" value="users">База пользователей</option>
                  <option name="informatics" value="informatics">База вопросов</option>
                  <option name="new" value="new">Новая база</option>
                </select>
                <div class="container-fluid mb-4 fade" data-id="new" hidden>
                    <div class="row align-items-center mb-4">
                        <div class="col-3">
                            Тип новой базы данных:
                        </div>
                        <div class="col-5">
                            <div class="button-group-vertical" role="group">
                                <input type="radio" class="btn-check" name="dbType" value="users" id="checkUsers">
                                <label class="btn btn-outline-info" for="checkUsers">База пользователей</label>
                                <input type="radio" class="btn-check" name="dbType" value="informatics" id="checkInf">
                                <label class="btn btn-outline-info" for="checkInf">База вопросов</label>
                            </div>
                        </div>
                    </div>
                    <div class="input-group mb-3">
                        <span class="input-group-text" id="spanNewDB">Имя новой базы данных:</span>
                        <input type="text" class="form-control" name="newDBName" aria-describedby="spanNewDB"> 
                    </div>
                    <div class="card-text fw-semibold mb-3">
                        <h6>Имя новой базы может содержать латинские символов, цифры или знак '_'. Длина от семи символов.</h6>
                        <h6>Например: <b>new_database_users</b></h6>
                    </div>
                </div>
            </form>
        </div>
        <div class="card-footer">
            <div class="container-fluid">
                <button class="btn btn-outline-primary pe-2" type="button" id="addNewDB" data-bs-toggle="modal" data-bs-target="#confirmAdd" disabled>Добавить базу данных</button>
                <button class="btn btn-outline-primary pe-2" type="button" id="clearDB" data-bs-toggle="modal" data-bs-target="#confirmClear" disabled>Очистить базу данных</button>
            </div>
        </div>
        <div id="modals">
            <div class="modal fade" id="confirmAdd" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false" aria-labelledby="confirmAddLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="confirmAddLabel">Вы уверены?</h1>
                        </div>
                        <div class="modal-body">
                            Убедитесь в том, что имя новой базы данных дано и содержит только латинские символы, цифры или символ "_".
                            Длина имени не должна быть менее семи символов.
                            Добавляя новую базу данных для пользователей, система автоматически добавит пользователя
                            Admin. Имя пользователя: admin, пароль: admin
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Нет</button>
                            <button type="button" class="btn btn-outline-primary" name="action" data-id="addNewDB" data-bs-dismiss="modal">Да</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal fade" id="confirmClear" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false" aria-labelledby="confirmClearLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="confirmClearLabel">Вы уверены?</h1>
                        </div>
                        <div class="modal-body">
                            При очистке базы данных с вопросами все вопросы удалятся безвозвратно!
                            При очистке базы данных для пользователей, система автоматически добавит пользователя
                            Admin. Имя пользователя: admin, пароль: admin
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Нет</button>
                            <button type="button" class="btn btn-outline-primary" name="action" data-id="clearDB" data-bs-dismiss="modal">Да</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
    forData.insertAdjacentHTML('beforeend', clearStructure);
    document.getElementById('dbType').addEventListener('change', handlerSelectType);
    document.getElementById('modals').addEventListener('click', handlerDBAction);
    for (let item of Array.from(forData.children)) {
        await sleep(100);
        item.classList.add('show');
    }
}

async function handlerSelectType(event) {
    let option = event.target.value;
    let newDbNameSection = document.querySelector('div[data-id="new"]');
    let clearDB = document.querySelector('button[id="clearDB"]');
    let addNewDB = document.querySelector('button[id="addNewDB"]');
    if (!option) {
        clearDB.disabled = true;
        addNewDB.disabled = true;
    } else if (option === 'new') {
        newDbNameSection.hidden = false;
        await sleep(100);
        newDbNameSection.classList.add('show');
        clearDB.disabled = true;
        addNewDB.disabled = false;
    } else {
        newDbNameSection.classList.remove('show');
        await sleep(200);
        newDbNameSection.hidden = true;
        addNewDB.disabled = true;
        clearDB.disabled = false;
    }
}

async function handlerDBAction(event) {
    let actions = {
        'addNewDB': addNewDB,
        'clearDB': clearDB
    };
    let clickedButton = event.target.closest('button[name="action"]');
    if (!clickedButton) return;
    let dbAction = clickedButton.dataset.id;
    await actions[dbAction]();
}

async function addNewDB() {
    let inputName = document.querySelector('input[name="newDBName"]');
    let dbType = document.querySelector('input[name="dbType"]:checked');
    if (!dbType) {
        createAlert(false, ['', 'Необходимо выбрать тип для новой базы данных'])
        return;
    }
    if (!inputName.value) {
        createAlert(false, ['', 'Необходимо ввести имя новой базы данных'])
        return;
    }
    const dbRegex = /^[a-zA-Z][a-zA-Z0-9_]{6,}$/;
    if (!dbRegex.test(inputName.value)) {
        createAlert(false, ['', '<b>Ошибка ввода!</b><br>Имя новой базы данных содержит недопустимые символы.']);
        return;
    }
    await createNewDB(inputName.value, dbType.value);
}

async function createNewDB(dbName, dbType) {
    let clickedButton = document.getElementById('addNewDB');
    clickedButton.innerHTML = `
    <div class="spinner-border spinner-border-sm text-primary ps-2" role="status"></div>
    <label>Добавляю...</label>
    `;
    clickedButton.disabled = true;
    try {
        const response = await fetch(`/databases/create/${dbType}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({database_name: dbName})
        });
        if (response.ok) {
            if (response.status === 201 || response.status === 200) {
                createAlert(true, ['База данных успешно создана.', '']);
            } else if (response.status === 404) {
                createAlert(false, ['', 'Во время создания базы произошли ошибки.']);
            }
        }
    } catch (error) {
        console.error(error);
    }
    clickedButton.innerHTML = `Добавить базу данных`;
    clickedButton.disabled = false;
}

async function clearDB() {
    let select = document.querySelector('select[id="dbType"]');
    let dbType = select.value
    let values = ['users', 'informatics'];
    if (!values.includes(dbType)) {
        createAlert(false, ['', 'Выберете корректный тип для очистки базы']);
        return;
    }
    let clickedButton = document.querySelector('button[id="clearDB"]');
    clickedButton.innerHTML = `
    <div class="spinner-border spinner-border-sm text-primary ps-2" role="status"></div>
    <label>Очищаю...</label>
    `;
    clickedButton.disabled = true;
    try {
        const response = await fetch(`/databases/clear/${dbType}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            if (response.status === 204 || response.status === 200) {
                createAlert(true, ['База данных успешно очищена.']);
            }
            if (response.status === 404) {
                createAlert(false, ['', 'Возникла ошибка. Проверьте выбранные поля.']);
            }
        }
    } catch (error) {
        console.error(error);
    }
    clickedButton.innerHTML = `Очистить базу данных`;
    clickedButton.disabled = false;
}

async function getActiveStudentsTestSessions() {
    let forData = document.querySelector('div[id="forData"]');
    forData.replaceChildren();
    forData.insertAdjacentHTML(
        'beforeend',
        `<h2 class="fw-bold fade">Список активных сессий тестов:</h2>`
    );
    let activeSessions = await getActiveSessions();
    console.log(activeSessions);
    if (activeSessions.length > 0) {
        activeSessions.forEach((session) => {
            let cardStructure = `
              <div class="card mb-2 overflow-x-auto fade" id="test-${session.ast_id}">
                <div class="card-body">
                    <div class="card-title">
                        <h5 class="card-title">
                            ${session.expired ? '<button class="btn btn-outline-danger">Время истекло</button>' : ''}
                        </h5>
                        <h5 class="card-title">
                            Сессия: ${session.name} (${session.username})
                        </h5>
                    </div>
                    <div class="row align-items-center">
                        <div class="col-10">
                            <p class="card-text"><b>Время начала:</b> ${new Date(session.start_time * 1000).toLocaleString()}</p>
                            <p class="card-text"><b>Время окончания:</b> ${new Date(session.stop_time * 1000).toLocaleString()}</p>
                            <p class="card-text"><b>Список id вопросов:</b> ${JSON.stringify(session.test)}</p>
                            <p class="card-text"><b>Список ответов на вопросы:</b> ${JSON.stringify(session.answers)}</p>
                        </div>
                        <div class="col-2">
                            <div class="btn-group-vertical" role="group">
                                ${session.expired ? `<button class="btn btn-outline-primary" id="${session.ast_id}" name="testSessionDelete" type="button">Удалить</button>` : ''}
                            </div>
                        </div>
                    </div>    
                </div>
              </div>
            `;
            forData.insertAdjacentHTML('beforeend', cardStructure);
        });
        forData.addEventListener('click', handlerTestSessionDelete);
    } else {
        forData.insertAdjacentHTML(
            'beforeend',
            `<h4 class="px-4 mt-4 fw-semibold fade">На данный момент активных сессий нет</h4>`
        );
    }
    for (let item of Array.from(forData.children)) {
        await sleep(50);
        item.classList.add('show');
    }
}

async function getActiveSessions() {
    try {
        const response = await fetch('/databases/active_tests_sessions', {
            method: "GET",
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            if (response.status === 404) {
                return null
            }
            const result = await response.json();
            return Array.from(result);
        }
    } catch (error) {
        console.error(error);
    }
}

async function handlerTestSessionDelete(event) {
    let buttonClick = event.target.closest('button[name="testSessionDelete"]');
    if (!buttonClick) return;
    let sessionId = buttonClick.id;
    await deleteTestSession(sessionId);
    let forData = document.getElementById('forData');
    forData.querySelector(`div[id="test-${sessionId}"]`);
}

async function deleteTestSession(sessionId) {
    try {
        const response = await fetch(`/databases/active_tests_sessions/${sessionId}`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            if (response.status === 204) {
                createAlert(true, ['Сессия теста успешно удалена.']);
                return true;
            } else if (response.status === 404) {
                createAlert(false, ['', 'Такой сессии теста не существует. Удаляем из списка.']);
                return false;
            }
        }
    } catch (error) {
        console.error(error);
    }
}

async function getActiveDatabaseList() {
    let archive = await getArchivedDatabases();
    console.log(archive);
    if (!archive) {
        createAlert(false, ['', 'Возникли проблемы с получением данных с сервера'])
        return;
    }
    let forData = document.querySelector('div[id="forData"]');
    let dbTypesStructure = `
    <div class="card mb-4 overflow-x-auto fade">
        <div class="card-header">
            <h3 class="card-title fw-semibold">
                Базы данных пользователей
            </h3>
        </div>
        <div class="card-body">
            <form id="dbInfData">
                <div class="card-text fw-bold mb-2">Выберите имя базы данных для активации:</div>
<!--                <select class="form-select mb-4" id="dbInfName" aria-label="Имя базы данных">-->
                  ${(() => {
                      let options = '<select class="form-select mb-4" id="dbInfName" aria-label="Имя базы данных">\n';
                      let structure = '<div class="container-fluid" id="infTableStructures">\n<div class="card-text mb-2">Структура таблиц:</div>\n'
                      Array.from(archive.informatics).forEach((item) => {
                          let name = item.main_db_name.MAIN_DB_INFORMATICS_NAME;
                          let baseStructure = item.db_structure;
                          options += `<option id="${name}" ${archive.active_i_db === name ? 'data-id="activeInf" selected' : ''}>${name}</option>\n`;
                          structure += `
                          <div name="${name}" ${archive.active_i_db === name ? '' : 'hidden'}>
                            <p class="fw-semibold mb-2">- ${baseStructure.INFORMATICS_DB_NAME}</p>
                          </div>
                          \n`;
                      });
                      options += '</select>\n';
                      structure += '</div>\n';
                      return `${options}\n${structure}`;
                  })()}
<!--                </select>-->
            </form>
        </div>
        <div class="card-footer">
            <div class="container-fluid">
                <button class="btn btn-outline-primary pe-2" type="button" id="dbInfActivation" disabled>Активировано</button>
            </div>
        </div>
    </div>
    <div class="card mb-4 fade">
        <div class="card-header">
            <h3 class="card-title fw-semibold">
                Базы данных с вопросами
            </h3>
        </div>
        <div class="card-body">
            <form id="dbUsersData">
                <div class="card-text fw-bold mb-2">Выберите имя базы данных для активации:</div>
<!--                <select class="form-select mb-4" id="dbUsersName" aria-label="Имя базы данных">-->
                  ${(() => {
                      let options = '<select class="form-select mb-4" id="dbUsersName" aria-label="Имя базы данных">\n';
                      let structure = '<div class="container-fluid" id="UsersTableStructures">\n<div class="card-text mb-2">Структура таблиц:</div>';
                      Array.from(archive.users).forEach((item) => {
                          // structure += '<div class="card-text mb-2">Структура таблиц:</div>\n';
                          let name = item.main_db_name.MAIN_DB_USERS_NAME;
                          let baseStructure = item.db_structure;
                          options += `<option id="${name}" ${archive.active_u_db === name ? 'data-id="activeUsers" selected' : ''}>${name}</option>\n`;
                          structure += `
                          <div name="${name}" ${archive.active_u_db === name ? '' : 'hidden'}>
                            <p class="fw-semibold mb-2">- ${baseStructure.USERS_DB_NAME}</p>
                            <p class="fw-semibold mb-2">- ${baseStructure.DAILY_STATISTICS_DB_NAME}</p>
                            <p class="fw-semibold mb-2">- ${baseStructure.USERS_STATISTICS_DB_NAME}</p>
                            <p class="fw-semibold mb-2">- ${baseStructure.ACTIVE_STUDENTS_TEST_DB_NAME}</p>
                          </div>
                          \n`;
                      });
                      options += '</select>\n';
                      structure += '</div>\n';
                      return `${options}\n${structure}`;
                  })()}
<!--                </select>-->
            </form>
        </div>
        <div class="card-footer">
            <div class="container-fluid">
                <button class="btn btn-outline-primary pe-2" type="button" id="dbUsersActivation" disabled>Активировано</button>
            </div>
        </div>
    </div>
    `;
    forData.insertAdjacentHTML('beforeend', dbTypesStructure);
    for (let item of Array.from(forData.children)) {
        await sleep(100);
        item.classList.add('show');
    }
    document.getElementById('dbInfName').addEventListener('change', handlerSelectDBInfName);
    document.getElementById('dbInfActivation').addEventListener('click', handlerDBInfNameActivation);
    document.getElementById('dbUsersName').addEventListener('change', handlerSelectDBUsersName);
    document.getElementById('dbUsersActivation').addEventListener('click', handlerDBUsersNameActivation);
}

async function getArchivedDatabases() {
    try {
        const response = await fetch('/databases/archived', {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        console.error(error);
    }
}

async function handlerSelectDBInfName(event) {
    let selectedValue = event.target.value;
    let option = document.getElementById(`${selectedValue}`);
    let dbNameActivationButton = document.getElementById('dbInfActivation');
    let dbStructures = document.querySelector('div[id="infTableStructures"]');
    Array.from(dbStructures.children).slice(1,).forEach((item) => {
        item.hidden = true;
    });
    let dbStructure = document.querySelector(`div[name="${selectedValue}"]`);
    dbStructure.hidden = false;
    if (option.dataset.id) {
        dbNameActivationButton.disabled = true;
        dbNameActivationButton.innerHTML = 'Активировано';
    } else {
        dbNameActivationButton.disabled = false;
        dbNameActivationButton.innerHTML = 'Активировать';
    }
}

async function handlerDBInfNameActivation() {
    let select = document.querySelector('select[id="dbInfName"]');
    let tableStructure = document.querySelector(`div[name="${select.value}"]`);
    let tablesNames = tableStructure.children[0].textContent.slice(2,);
    // Array.from(tableStructure.children).forEach((tableName) => {
    //     tablesNames.push(tableName.textContent.slice(2,));
    // });
    console.log('proceed activation');
    try {
        const response = await fetch('/databases/archives', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({db_type: 'informatics', db_structure: {
                    MAIN_DB_INFORMATICS_NAME: select.value,
                    INFORMATICS_DB_NAME: tablesNames
                }})
        });
        if (response.ok) {
            let status = response.status;
            if ([204, 200].includes(status)) {
                let activatedButton = document.getElementById('dbInfActivation');
                activatedButton.disabled = true;
                activatedButton.innerHTML = 'Активировано';
                let active = document.querySelector('option[data-id="activeInf"]');
                active.removeAttribute('data-id');
                document.getElementById(`${select.value}`).dataset.id = 'activeInf';
                createAlert(true, [`База данных ${select.value} успешно активирована`]);
            } else if (status === 404) {
                createAlert(false, ['', 'Во время активации базы произошли ошибки'])
            }

        }
    } catch (error) {
        console.error(error);
    }
}

async function handlerSelectDBUsersName(event) {
    let selectedValue = event.target.value;
    let option = document.getElementById(`${selectedValue}`);
    let dbNameActivationButton = document.getElementById('dbUsersActivation');
    let dbStructures = document.querySelector('div[id="UsersTableStructures"]');
    Array.from(dbStructures.children).slice(1,).forEach((item) => {
        item.hidden = true;
    });
    let dbStructure = document.querySelector(`div[name="${selectedValue}"]`);
    dbStructure.hidden = false;
    if (option.dataset.id) {
        dbNameActivationButton.disabled = true;
        dbNameActivationButton.innerHTML = 'Активировано';
    } else {
        dbNameActivationButton.disabled = false;
        dbNameActivationButton.innerHTML = 'Активировать';
    }
}

async function handlerDBUsersNameActivation() {
    let select = document.querySelector('select[id="dbUsersName"]');
    // console.log(select.value);
    let tableStructure = document.querySelector(`div[name="${select.value}"]`);
    let tablesNames = [];
    Array.from(tableStructure.children).forEach((tableName) => {
        tablesNames.push(tableName.textContent.slice(2,));
    });
    // console.log(tablesNames);
    try {
        const response = await fetch('/databases/archives', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({db_type: 'users', db_structure: {
                    MAIN_DB_USERS_NAME: select.value,
                    USERS_DB_NAME: tablesNames[0],
                    DAILY_STATISTICS_DB_NAME: tablesNames[1],
                    USERS_STATISTICS_DB_NAME: tablesNames[2],
                    ACTIVE_STUDENTS_TEST_DB_NAME: tablesNames[3]
                }})
        });
        if (response.ok) {
            let status = response.status;
            if ([204, 200].includes(status)) {
                let activatedButton = document.getElementById('dbUsersActivation');
                activatedButton.disabled = true;
                activatedButton.innerHTML = 'Активировано';
                let active = document.querySelector('option[data-id="activeUsers"]');
                active.removeAttribute('data-id');
                document.getElementById(`${select.value}`).dataset.id = 'activeUsers';
                createAlert(true, [`База данных ${select.value} успешно активирована`]);
            } else if (status === 404) {
                createAlert(false, ['', 'Во время активации базы произошли ошибки'])
            }

        }
    } catch (error) {
        console.error(error);
    }
}
