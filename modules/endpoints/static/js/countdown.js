function countdownTimer(test_time) {
    let time = test_time; // Задаём начальное время
    while (time > -11) {
        setInterval(() => {
        if (time == 300) {
          document.getElementById('clock').className = "btn btn-outline-warning";
        }
        else if (time == 120) {
          document.getElementById('clock').className = "btn btn-outline-danger";
        }
        if (time > 0) {
          document.getElementById('countdown').textContent = ('0' + Math.floor(time/60)).slice(-2) + " : " + ('0' + Math.floor(time % 60)).slice(-2);
        }
        else if (time == 0) {
          document.getElementById('countdown').textContent = "Необходимо закончить тест";
        }
        else if (time <= -10) {
          document.getElementById('finish').click();
         }
          time--; // С каждой секундой уменьшаем время
      }, 990); // Интервал делаем одной секунды
  };
}
