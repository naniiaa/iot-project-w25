var temperatureThreshold = 35;
var lightThreshold = 2000;
var currentProfile;

var animateValue = function animateValue (newPercent, elem) {
    //elem = elem || $('#fu-percent span');
    const val = parseInt(elem.text(), 10);

    if(val !== parseInt(newPercent, 10)) {
        let diff = newPercent < val ? -1 : 1;
        elem.text(val + diff);
        setTimeout(animateValue.bind(null, newPercent, elem), 5);
    }
}; 

function setHumidity(newHum)
{
const amount = Math.ceil(newHum || 25);
const currentPercent = $('#fu-percent span').text();
const waterAnimSpeed = (Math.abs(currentPercent - amount) / 50) * 10;
const waterPercent = 100 - amount;
animateValue(amount, $('#fu-percent span'));
$('#water').css({
  top : waterPercent + '%'
});
}
  
function setTemperature(temp) {

    if (temp < 0 || temp > 40) {
        return;
    }

    let value = temp/40

    $('#gauge__fill').css('transform', `rotate(${ value / 2 }turn)`);
    animateValue(temp, $('#gauge__cover'));

    if (value < 0.5) {
        document.querySelector("#gauge__fill").style.backgroundColor = 'blue';
    } else {
        document.querySelector("#gauge__fill").style.backgroundColor = 'red';
    }

}

var slider = document.getElementById("LED_slider");
var output = document.getElementById("LB-cover");
var output_value = document.getElementById("LEDValue");
var notif = document.getElementById("notif");
var sentEmail = false;

function clearNotification()
{
    $("#img_notif").attr('src', "../static/MailIdle.png")
    notif.innerHTML = "";
}

async function updateHumTemp() {
    try {
        const response = await fetch('/temp-hum');
        
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        const tempData = parseFloat(data.temperature);
        const humData = parseFloat(data.humidity);

        if (isNaN(tempData) && isNaN(humData)) {
            throw new Error('Invalid data received from the server.');
        }

        setHumidity(humData);
        setTemperature(tempData);

        if (data.fan) {
            fanImg.src = fanOn_url;
            fanImg.classList.add("spin_animation");
        } else {
            fanImg.classList.remove("spin_animation");
            fanImg.src = fanOff_url;
        }

    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

fanImg.addEventListener('click', async () => {
    try {
        const response = await fetch('/toggle-off');

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('Fan toggled successfully:', data); 

        

    } catch (error) {
        console.error('Error toggling fan:', error);
    }
});

function transmitData()
{
    //updateProfile();
    //updateLED();
    updateHumTemp();
}

transmitData();
setInterval(transmitData, 1000);
