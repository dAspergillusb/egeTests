function changeValue(inputId, buttonId) {
  var buttonName = document.getElementById(buttonId).name;
  var input = document.getElementById(inputId);
  var value = parseInt(input.value);
  if (buttonName == 'up') {
    input.value = value + 1;
  };
  if (buttonName == 'down') {
    if (input.value > 0) {
      input.value = value - 1;
    };
  };
  if (input.value > 0) {
    document.getElementById('down_' + input.name.slice(-1)).disabled = false;
  };
  if (input.value == 0) {
    document.getElementById('down_' + input.name.slice(-1)).disabled = true;
  };
  if (input.value == 10) {
    document.getElementById('up_' + input.name.slice(-1)).disabled = true;
  };
  if (input.value < 10) {
    document.getElementById('up_' + input.name.slice(-1)).disabled = false;
  };

  var commonSum = 0;
  for (let i = 1; i < 28; i++) {
    var inputValue = document.getElementById('q_' + i);
    commonSum += parseInt(inputValue.value);
  };
  if (commonSum >= 30) {
    for (let i = 1; i < 28; i++) {
      var button = document.getElementById('up_' + i);
      button.disabled = true;
    };
  } else {
    for (let i = 1; i < 28; i++) {
      if (document.getElementById('q_' + i).value < 10) {
        var button = document.getElementById('up_' + i);
        button.disabled = false;
        };
      };
  };
};
