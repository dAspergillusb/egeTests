function valueUp(input) {
    input.setAttribute('value', parseInt(input.value) + 1)
}

function valueDown(input) {
    if (input.value > 0) {
        input.setAttribute('value', parseInt(input.value) - 1)
    }
}

function buttonDisabled(button) {
    button.disabled = true;
}

function buttonEnabled(button) {
    button.disabled = false;
}

function changeValue(inputId, buttonId) {
    const buttonName = document.getElementById(buttonId).name;
    const input = document.getElementById(inputId);
    const upDown = {
      'up': valueUp,
      'down': valueDown
    };
    upDown[buttonName](input);

    const buttonDown = document.getElementById(`down_${inputId.slice(2,)}`);
    const buttonUp = document.getElementById(`up_${inputId.slice(2,)}`);
    const buttonUpEvents = {
        [parseInt(input.value) === 10]: buttonDisabled,
        [parseInt(input.value) < 10]: buttonEnabled
    }
    const buttonDownEvents = {
      [parseInt(input.value) > 0]: buttonEnabled,
      [parseInt(input.value) === 0]: buttonDisabled
    }
    buttonUpEvents[true](buttonUp);
    buttonDownEvents[true](buttonDown);

    var commonSum = 0;
    const inputs = document.querySelectorAll('input[name^="q_"][type="text"]');
    inputs.forEach(input => {
        commonSum += parseInt(input.value);
    })
    var buttons = document.querySelectorAll('button[name="up"]');
    if (commonSum >= 30) {
        buttons.forEach(button => {
            button.disabled = true;
        });
    } else {
        buttons.forEach(button => {
            if (document.getElementById(`q_${button.id.slice(3,)}`).value < 10) {
                button.disabled = false;
            }
        });
      }
}
