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
let lastEmailSent = false;
let currentEmailSent = false;

$("#img_notif").addClass('active');

function clearNotification() {
    $("#img_notif").attr('src', "../static/MailIdle.png");
    $("#img_notif").removeClass('active');
    notif.innerHTML = "";
}

async function updateHumTemp() {
    try {
        const response = await fetch('/temp-hum');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (!data.hasOwnProperty('temperature') || !data.hasOwnProperty('humidity')) {
            console.error("Missing temperature or humidity in the response:", data);
            return; // Early Exit
        }

        const tempData = data.temperature !== null ? parseFloat(data.temperature) : null;
        const humData = data.humidity !== null ? parseFloat(data.humidity) : null;

        if ((tempData === null || isNaN(tempData)) && (humData === null || isNaN(humData))) {
            console.error("Invalid temperature and humidity values from server", {
                rawTemp: data.temperature,
                parsedTemp: tempData,
                rawHum: data.humidity,
                parsedHum: humData
            });
            return; // Early Exit
        }

        if (tempData !== null && !isNaN(tempData)) {
            setTemperature(tempData);
        }
        
        if (humData !== null && !isNaN(humData)) {
            setHumidity(humData);
        }

        // Check for email status
        if (data.hasOwnProperty('email_sent')) {
            console.log("Email status:", data.email_sent);
            updateMailNotification(data.email_sent);
        }

        // Update fan status on the dashboard
        if (data.hasOwnProperty('fan')) {
            console.log("Fan status:", data.fan);
            if (data.fan) {
                fanImg.src = "../static/FanOn.png";
                fanImg.classList.add("spin_animation");
            } else {
                fanImg.src = "../static/FanOff.png";
                fanImg.classList.remove("spin_animation");
            }
        }

    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

function updateMailNotification(isEmailSent) {
    const imgElement = document.getElementById('img_notif');
    const notifElement = document.getElementById('notif');
    
    if (isEmailSent) {
        // Shows that at email has been sent
        imgElement.src = "../static/MailSent.png";
        notifElement.innerHTML = "Email sent!";
    } else {
        // No email or idle state
        imgElement.src = "../static/MailIdle.png";
        notifElement.innerHTML = "";
    }
}

fanImg = document.getElementById('fanIcon');

fanImg.addEventListener('click', async () => {
    try {
        const response = await fetch('/toggle-off');

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const result = await response.json();
        console.log('Fan toggled successfully:', result);
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