
var temperatureThreshold = 35;
var lightThreshold = 2000;
var currentProfile;

const fanImg = document.getElementById('fanIcon');

function loadBars() //document.addEventListener("load", function()
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

function setTHMeters(T_Value=0, H_Value=0)
{
    const temperature_meter = document.getElementById("TemperatureMeter").getElementsByClassName("Bar");
    const humidity_meter = document.getElementById("HumidityMeter").getElementsByClassName("Bar");
    
    console.log('loggin');

    if (temperature_meter && humidity_meter)
    {
        T_Value = Math.random()*40;
        H_Value = Math.random()*40;

        newData(T_Value, H_Value);

        for (let i = 0; i < 40; i++)
            {
                let bar = temperature_meter[i];
                let bar2 = humidity_meter[i];
                bar.style.opacity = 0.25;
                bar2.style.opacity = 0.25;
                bar.style.backgroundColor = "white";
                bar2.style.backgroundColor = "white";
            }

        for (let i = 0; i < T_Value; i++)
            {
                let bar = temperature_meter[39-i];
                bar.style.opacity = 1;
                bar.style.backgroundColor = "red";
                document.getElementById("TemperatureMeterCounter").innerHTML = Math.floor(T_Value) + " °C";
            }

        for (let i = 0; i < H_Value; i++)
            {
                let bar = humidity_meter[39-i];
                bar.style.opacity = 1;
                bar.style.backgroundColor = "cyan";
                document.getElementById("HumidityMeterCounter").innerHTML = Math.floor(H_Value) + "%";
            }
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

        if (data.fan) {
            fanImg.src = "../static/FanOn.png";;
            fanImg.classList.add("spin_animation");
        } else {
            fanImg.src = "../static/FanOff.png";;
            fanImg.classList.remove("spin_animation");        
        }

    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

async function updateLED() {
    try {
        const response = await fetch('/LED');
        
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        const LED_Intensity = parseFloat(data.intensity);
        
        if (isNaN(LED_Intensity)) {
            throw new Error('Invalid data received from the server.');
        }

        output.style.opacity = (LED_Intensity/5000);
        output_value.innerHTML = LED_Intensity;
        slider.value = LED_Intensity;

        if (LED_Intensity < lightThreshold)
        {        
            $("#img_notif").attr('src', "../static/MailSent.png")
            notif.innerHTML = "Email sent."
            if (sentEmail == false)
            {
                sentEmail = true;
                setTimeout(clearNotification, 1000);
            }
        }
        else
        {
            sentEmail = false;
        }

    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

async function updateProfile()
{
    try {
        const response = await fetch('/profile');
        
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const profileData = await response.json();
        

        temperatureThreshold = (profileData.data["temperature_threshold"]);
        lightThreshold = (profileData.data["intensity_threshold"])
        
        if (isNaN(temperatureThreshold) && isNaN(lightThreshold)) {
            throw new Error('Invalid data received from the server.');
        }

        if (!currentProfile || (profileData.userID != currentProfile.userID))
        {
            console.log("PP: " + currentProfile)
            currentProfile = profileData;
            $("#profile_img").attr('src', currentProfile.data["profile_image"]);
            $("#profile_name").text("User: " + currentProfile.data["username"]);
            $("#TT").text(`Temperature Threshold: ${temperatureThreshold} °C`);
            $("#LT").text(`Light Threshold: ${lightThreshold}`);
        
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

//=================================================================== Graph


const xValues = [0,5,10,15,20,25,30,35,40,45,50,55,60];

const temperature_data = [];//[860,1140,1060,1060,1070,1110,1330,2210,7830,2478];
const humidity_data = [];//[300,700,2000,5000,6000,4000,2000,1000,200,100];

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

let newX = 0;

function setThreshold(TT, HT)
{
  temp_treshold.splice(0);
  hum_treshold.splice(0);
  for (i = 0; i < 13; i++)
  {
    temp_treshold.push(22);
    hum_treshold.push(5);
  }
}

function newData(CurrentTemperature = 0, CurrentHumidity = 0)
{
	/*let lastData = xValues[xValues.length - 1];
    xValues.shift();
    xValues.push(lastData + 100);
    temperature_data.shift();
    humidity_data.shift();*/
    switch(CurrentHumidity)
    {
      case CurrentHumidity>40:
        CurrentHumidity = 40;
        break;
      case CurrentHumidity<0:
        CurrentHumidity = 0;
        break;
      default:
        break;
    }

    switch(CurrentTemperature)
    {
      case CurrentTemperature>40:
        CurrentHumidity = 40;
        break;
      case CurrentTemperature<-10:
        CurrentHumidity = -10;
        break;
      default:
        break;
    }

    if (newX >= 13)
    {
        let lastData = xValues[xValues.length - 1];
        xValues.shift();
        xValues.push(lastData + 5);
        //newX -= 50;
    }
    
    newX++;
    if (temperature_data.length >= 13 && humidity_data.length >= 13)
    {
        temperature_data.shift();
        humidity_data.shift();
    }
    
    temperature_data.push({x: newX/10, y: CurrentTemperature});
    humidity_data.push({x: newX/10, y: CurrentHumidity});
    
    chart.update("none");
}

function transmitData()
{
    updateProfile();
    updateLED();
    updateHumTemp();
}

setThreshold();

//setTHMeters(22, 12);
loadBars();

//setTimeout(setTHMeters(22, 12), 2000);
//transmitData();
setInterval(setTHMeters, 500);
