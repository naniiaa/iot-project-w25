var temperatureThreshold = 35;
var lightThreshold = 400;
var currentProfile;

// var slider = document.getElementById("LED_slider");
// var output = document.getElementById("LB-cover");
// var output_value = document.getElementById("LEDValue");

var notif = document.getElementById("notif");

var sentEmail = false;
let lastEmailSent = false;
let currentEmailSent = false;


// Initialize light bulb images
const LIGHT_OFF_IMG = "../static/LightOff.png";
const LIGHT_ON_IMG = "../static/LightOn.png";

// $("#img_notif").addClass('active');

function clearNotification() {
    $("#img_notif").attr('src', "../static/MailIdle.png");
    $("#img_notif").removeClass('active');
    notif.innerHTML = "";
}

function loadBars()
{
    console.log("Loaded");
    const containers = document.getElementsByClassName("BarContainer");

    for (let i = 0; i < containers.length; i++) {
        
            const tempDB = containers.item(i);

            for (let i = 0; i < 40; i++) {
                console.log("Loading");
                const bar = document.createElement("div");
                bar.className = "Bar";
                bar.id = `Bar_${40-i}`;
                tempDB.appendChild(bar);
            }

            const counter = document.createElement("div");
            counter.className = "MeterCounter";
            counter.id = tempDB.id + "Counter";
            tempDB.appendChild(counter);

        }
};

function isInRange(value, min, max)
{
    if (value > min && value < max)
    {
        return true;
    }
    return false;
}

let last_Temp = 0;
let last_Hum = 0;

function setTHMeters(T_Value=0, H_Value=0)
{
    const temperature_meter = document.getElementById("TemperatureMeter").getElementsByClassName("Bar");
    const humidity_meter = document.getElementById("HumidityMeter").getElementsByClassName("Bar");
	
    if (temperature_meter && humidity_meter)
    {

	if (isInRange(T_Value, 0, 40) && isInRange(H_Value, 0, 100))
        {
        	newData(T_Value, H_Value);
		last_Temp = T_Value;
		last_Hum = H_Value;
        }
	else
	{
		newData(last_Temp, last_Hum);
	}

        for (let i = 0; i < 40; i++)
            {
                let bar = temperature_meter[i];
                let bar2 = humidity_meter[i];
                bar.style.opacity = 0.25;
                bar2.style.opacity = 0.25;
                bar.style.backgroundColor = "white";
                bar2.style.backgroundColor = "white";
            }

        for (let i = 0; i < last_Temp; i++)
            {
                let bar = temperature_meter[39-i];
                bar.style.opacity = 1;
                bar.style.backgroundColor = "red";
                document.getElementById("TemperatureMeterCounter").innerHTML = Math.floor(last_Temp) + " °C";
            }

	let humidity_bar_percentage = Math.floor(40 * (last_Hum/100));
	    
        for (let i = 0; i < humidity_bar_percentage; i++)
            {
                let bar = humidity_meter[39-i];
                bar.style.opacity = 1;
                bar.style.backgroundColor = "cyan";
                document.getElementById("HumidityMeterCounter").innerHTML = Math.floor(last_Hum) + "%";
            }
    }
}

/*================ LIGHT =================================*/
let last_Light = 0;

// Update light intensity 
function updateLightVisualization(intensity, ledStatus) {

    // INTENSITY
    const lightIntensityElement = document.getElementById("light-intensity");
    if (lightIntensityElement) {
        lightIntensityElement.textContent = intensity;
    }
    
    // STATUS
    const ledStatusElement = document.getElementById("led-status");
    if (ledStatusElement) {
        ledStatusElement.textContent = ledStatus;
        ledStatusElement.className = ledStatus === "ON" ? "on" : "off";
    }

    // LIGHTBULB
    const lightBulbImage = document.getElementById("light-bulb-img");
    if (lightBulbImage) {
        lightBulbImage.src = ledStatus === "ON" ? "/static/LightOn.png" : "/static/LightOff.png";
        lightBulbImage.classList.remove("on");
        if (ledStatus === "ON") {
            lightBulbImage.classList.add("on");
        }
        
        console.log(`Light bulb updated: status=${ledStatus}, src=${lightBulbImage.src}, classes=${lightBulbImage.className}`);
    }
    
    // LIGHT NETER
    const lightMeterFill = document.getElementById("light-meter-fill");
    if (lightMeterFill) {
        // Calculate percentage (0-2000 range)
        const percentage = Math.min(100, Math.max(0, (intensity / 2000) * 100));
        lightMeterFill.style.width = percentage + "%";
    }

    const thresholdValue = document.getElementById('threshold-value');
    if(thresholdValue)
    {
        thresholdValue.textContent = lightThreshold;
    }
}

// Fetch light intensity
async function updateLightData() {
    try {
        const response = await fetch('/light-data');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Update light intensity
        if (data.hasOwnProperty('light_intensity') && data.hasOwnProperty('led_status')) {
            const lightIntensity = data.light_intensity;
            const ledStatus = data.led_status;

            last_Light = lightIntensity;
            
            // Update visualizations
            updateLightVisualization(lightIntensity, ledStatus);
        }
        
        // Update threshold display
        if (data.hasOwnProperty('light_threshold')) {
            const thresholdValue = document.getElementById('threshold-value');
            if (thresholdValue) {
                thresholdValue.textContent = data.light_threshold;
                lightThreshold = data.light_threshold;
            }
        }
        
        // Check for email status
        if (data.hasOwnProperty('light_email_sent')) {
            const isEmailSent = data.light_email_sent;
            const imgElement = document.getElementById('img_notif');
            const notifElement = document.getElementById('notif');
            
            if (isEmailSent) {
                imgElement.src = "../static/MailSent.png";
                notifElement.innerHTML = "Light Alert Email sent!";
                imgElement.classList.add('active');
            } else {
                imgElement.src = "../static/MailIdle.png";
                notifElement.innerHTML = "Email has not been sent";
                imgElement.classList.remove('active');
            }
        }
        
    } catch (error) {
        console.error('Error fetching light data:', error);
    }
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

        if ((tempData !== null && !isNaN(tempData)) && (humData !== null && !isNaN(humData))) {
            setTHMeters(tempData, humData)
        }

        // Check for email status
        if (data.hasOwnProperty('email_sent')) {
            console.log("Email status:", data.email_sent);
            updateMailNotification(data.email_sent);
        }

        // Update fan status on the dashboard
        if (data.hasOwnProperty('fan')) {
            console.log("Fan status:", data.fan);
            if (data.fan == true) {
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

/*================ MAIL NOTIF =================================*/
function updateMailNotification(isEmailSent) {
    const imgElement = document.getElementById('img_notif');
    const notifElement = document.getElementById('notif');
    
    if (isEmailSent) {
        // Shows that at email has been sent
        imgElement.src = "../static/MailSent.png";
        notifElement.innerHTML = "Email sent!";
        imgElement.classList.add('active');
    } else {
        // No email or idle state
        imgElement.src = "../static/MailIdle.png";
        notifElement.innerHTML = "";
        imgElement.classList.remove('active');
    }
}

fanImg = document.getElementById('fanIcon');

fanImg.addEventListener('click', async () => {
    try {
        const response = await fetch('/toggle-off');

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        fanImg.src = "../static/FanOff.png";
        fanImg.classList.remove("spin_animation");
        
        const result = await response.json();
        console.log('Fan toggled successfully:', result);
    } catch (error) {
        console.error('Error toggling fan:', error);
    }
});

//=================================================================== Graph


const xValues = [];

const temperature_data = [];
const humidity_data = [];

const temp_treshold = [];
const hum_treshold = [];

const chart = new Chart("myChart", {
      type: "line",
      data: {
        labels: xValues,
        datasets: [{ 
          data: temperature_data,
          lineTension: 0,
          borderColor: "red",
          fill: false,
        }, { 
          data: humidity_data,
          lineTension: 0,
          borderColor: "blue",
          fill: false,
        }, { 
          data: temp_treshold,
          lineTension: 0,
          borderColor: "pink",
          fill: false,
          pointStyle: "line"
        }, { 
          data: hum_treshold,
          lineTension: 0,
          borderColor: "violet",
          fill: false,
          pointStyle: "line"
        }]
      },
      options: {
        legend: {display: false},
        animation: false
      }
    });
Chart.defaults.global.defaultFontColor = "#fff";

let newX = 0;

function setThreshold(TT, HT)
{
  temp_treshold.splice(0);
  hum_treshold.splice(0);
  for (i = 0; i < 13; i++)
  {
    temp_treshold.push(23);
    hum_treshold.push(15);
  }
}

function newData(CurrentTemperature = 0, CurrentHumidity = 0)
{
	if (newX >= 13)
    {
        let lastData = xValues[xValues.length - 1];
        xValues.shift();     
        //newX -= 50;
    }
    else
    {
        newX++;
    }
    
    let now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let seconds = now.getSeconds();
    xValues.push(`${hours}:${minutes}:${seconds}|`);
	
    if (temperature_data.length >= 13 && humidity_data.length >= 13)
    {
        temperature_data.shift();
        humidity_data.shift();
    }
    
    temperature_data.push({x: newX/10, y: CurrentTemperature});
    humidity_data.push({x: newX/10, y: CurrentHumidity});
    
    chart.update("none");
}

function logData()
{
    console.log("Light intensity:", last_Light);
    console.log("LED Status:", document.getElementById("led-status").textContent);
    console.log("Threshold", lightThreshold);
}
// Update function to call both data updates
function updateAllData() {
    updateHumTemp();
    updateLightData();
    logData();
}

setThreshold();
loadBars();
//transmitData();
setInterval(updateAllData, 1000);

