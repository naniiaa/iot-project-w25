document.addEventListener('DOMContentLoaded', function() {
    var temperatureThreshold = 24;
    var lightThreshold = 2000;
    var currentProfile;
  
    let lastRFIDtag = "";
    var notif = document.getElementById("notif");
  
    var sentEmail = false;
    let lastEmailSent = false;
    let currentEmailSent = false;
  
    const LIGHT_OFF_IMG = "../static/LightOff.png";
    const LIGHT_ON_IMG = "../static/LightOn.png";
  

    let lastRfidTag = "";
    let rfidAnimationTimeout = null;
  
    function clearNotification() {
      document.getElementById("img_notif").src = "../static/MailIdle.png";
      document.getElementById("img_notif").classList.remove('active');
      notif.innerHTML = "";
    }
  
    function loadBars() {
    console.log("Loading bar containers...");
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
        }
    };
  
    function forceProfileUpdate() {
      currentProfile = null;
      updateProfile(true);
    }

    async function updateRFIDData() {
      try {
        const response = await fetch('/rfid-data');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const rfidData = await response.json();
        
        if (rfidData) {
          // Check if the RFID tag has changed
          if (rfidData.rfid_tag && rfidData.rfid_tag !== lastRfidTag) {
            console.log("New RFID tag detected:", rfidData.rfid_tag);
            lastRfidTag = rfidData.rfid_tag;
            
            forceProfileUpdate();

            // Animate the RFID changes
            document.getElementById("user-profile").classList.add("rfid-active")
            if (rfidAnimationTimeout) clearTimeout(rfidAnimationTimeout);
            rfidAnimationTimeout = setTimeout(() => {
              document.getElementById("user-profile").classList.remove("rfid-active");
            }, 3000);
          }
          
          // Update RFID tag
          document.getElementById('rfid_tag').textContent = rfidData.rfid_tag || '--';
          
          // Update user profile
          document.getElementById('profile_username').textContent = rfidData.username || 'Unknown';
          document.getElementById('profile_name').textContent = "User: " + (rfidData.username || 'Unknown');
          
          // Update profile image
          if (rfidData.profile_image) {
            const profileImages = document.querySelectorAll('.profile-img');
            profileImages.forEach(img => {
              img.src = rfidData.profile_image;
            });
          }
          
          // Update last entry time
          // document.getElementById('last_entry').textContent = rfidData.timestamp || '--';

          // Update last entry time
          const lastEntry = document.getElementById('last_entry');
          if (lastEntry) {
            lastEntry.textContent = rfidData.timestamp || '--';
          }
          
          // Update thresholds
          if (rfidData.temperature_threshold) {
            document.getElementById('user_temp_threshold').textContent = rfidData.temperature_threshold;
            temperatureThreshold = rfidData.temperature_threshold;
            
            const tempThresholdElement = document.getElementById("TT");
            if (tempThresholdElement) {
              tempThresholdElement.textContent = `Temperature Threshold: ${temperatureThreshold} °C`;
            }
          }
          
          if (rfidData.intensity_threshold) {
            document.getElementById('user_light_threshold').textContent = rfidData.intensity_threshold;
            lightThreshold = rfidData.intensity_threshold;
            
            const lightThresholdElement = document.getElementById("LT");

            if (lightThresholdElement) {
              lightThresholdElement.textContent = `Light Threshold: ${lightThreshold}`;
            }
            
            const thresholdValueElement = document.getElementById('threshold-value');
            if (thresholdValueElement) {
              thresholdValueElement.textContent = `${lightThreshold}`;
            }
          }
        }
      } catch (error) {
        console.error('Error fetching RFID data:', error);
      }
    }
  
    async function updateProfile(forceUpdate = false) {
      try {
        console.log("Updating profile, force update:", forceUpdate);
        
        const response = await fetch('/profile');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const profileData = await response.json();
        console.log("Profile data received:", profileData);
        
        if (profileData) {
          // Extract data with proper structure handling
          let tempThreshold = 0;
          let lightThreshold = 0;
          let username = "Unknown";
          let profileImage = "";
          
          if (profileData.data) {
            // Normal 
            tempThreshold = profileData.data.temperature_threshold;
            lightThreshold = profileData.data.intensity_threshold;
            username = profileData.data.username;
            profileImage = profileData.data.profile_image;
          } else {
            // Alt
            tempThreshold = profileData.tempThreshold;
            lightThreshold = profileData.lightThreshold;
          }
          
          //  Check for changes
          if (forceUpdate || !currentProfile || 
              (profileData.userID !== currentProfile.userID) ||
              (tempThreshold !== temperatureThreshold) ||
              (lightThreshold !== lightThreshold)) {
            
            console.log("Updating profile display - values changed");
            
            // Update variables
            temperatureThreshold = tempThreshold;
            lightThreshold = lightThreshold;
            currentProfile = profileData;
            
            // Update UI
            if (profileImage) {
              const profileImgs = document.querySelectorAll("#profile_img, #profile_image");
              profileImgs.forEach(img => {
                img.src = profileImage;
              });
            }
            
            // Update text elements
            const profileNameElement = document.getElementById("profile_name");
            if (profileNameElement) {
              profileNameElement.textContent = "User: " + username;
            }
            
            const profileUsernameElement = document.getElementById("profile_username");
            if (profileUsernameElement) {
              profileUsernameElement.textContent = username;
            }
            
            const userTempThresholdElement = document.getElementById("user_temp_threshold");
            if (userTempThresholdElement) {
              userTempThresholdElement.textContent = temperatureThreshold;
            }
            
            const userLightThresholdElement = document.getElementById("user_light_threshold");
            if (userLightThresholdElement) {
              userLightThresholdElement.textContent = lightThreshold;
            }
            
            const ttElement = document.getElementById("TT");
            if (ttElement) {
              ttElement.textContent = `Temperature Threshold: ${temperatureThreshold} °C`;
            }
            
            const ltElement = document.getElementById("LT");
            if (ltElement) {
              ltElement.textContent = `Light Threshold: ${lightThreshold}`;
            }
            
            const thresholdValueElement = document.getElementById("threshold-value");
            if (thresholdValueElement) {
              thresholdValueElement.textContent = lightThreshold;
            }
          } else {
            console.log("No profile changes detected");
          }
        }
      } catch (error) {
        console.error('Error fetching profile data:', error);
      }
    }
  
    function isInRange(value, min, max) {
      if (value > min && value < max) {
        return true;
      }
      return false;
    }
  
    let last_Temp = 0;
    let last_Hum = 0;
  
    function setTHMeters(T_Value=0, H_Value=0) {
      const temperature_meter = document.getElementById("TemperatureMeter").getElementsByClassName("Bar");
      const humidity_meter = document.getElementById("HumidityMeter").getElementsByClassName("Bar");
      
      if (temperature_meter && humidity_meter) {
        if (isInRange(T_Value, 0, 40) && isInRange(H_Value, 0, 100)) {
          newData(T_Value, H_Value);
          last_Temp = T_Value;
          last_Hum = H_Value;
        } else {
          newData(last_Temp, last_Hum);
        }
  
        for (let i = 0; i < 40; i++) {
          let bar = temperature_meter[i];
          let bar2 = humidity_meter[i];
          bar.style.opacity = 0.25;
          bar2.style.opacity = 0.25;
          bar.style.backgroundColor = "white";
          bar2.style.backgroundColor = "white";
        }
  
        for (let i = 0; i < last_Temp; i++) {
          let bar = temperature_meter[39-i];
          bar.style.opacity = 1;
          bar.style.backgroundColor = "red";
          document.getElementById("TemperatureMeterCounter").innerHTML = Math.floor(last_Temp) + " °C";
        }
  
        let humidity_bar_percentage = Math.floor(40 * (last_Hum/100));
        
        for (let i = 0; i < humidity_bar_percentage; i++) {
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
        lightBulbImage.src = ledStatus === "ON" ? LIGHT_ON_IMG : LIGHT_OFF_IMG;
        lightBulbImage.classList.remove("on");
        if (ledStatus === "ON") {
          lightBulbImage.classList.add("on");
        }
        
        console.log(`Light bulb updated: status=${ledStatus}, src=${lightBulbImage.src}, classes=${lightBulbImage.className}`);
      }
      
      // LIGHT METER
      const lightMeterFill = document.getElementById("light-meter-fill");
      if (lightMeterFill) {
        // Calculate percentage (0-4000 range)
        const percentage = Math.min(100, Math.max(0, (intensity / 4000) * 100));
        lightMeterFill.style.width = percentage + "%";
      }
  
      const thresholdValue = document.getElementById('threshold-value');
      if(thresholdValue) {
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
          const imgElement = document.getElementById('led_img_n');
          const notifElement = document.getElementById('ledspannotif');
          console.log(`${isEmailSent}==================`);
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
          setTHMeters(tempData, humData);
        }
  
        // Check for email status
        if (data.hasOwnProperty('email_sent')) {
          console.log("Email status:", data.email_sent);
          updateMailNotification(data.email_sent);
        }
  
        // Update fan status on the dashboard
        /*if (data.hasOwnProperty('fan')) {
          console.log("Fan status:", data.fan);
          const fanImg = document.getElementById('fanIcon');
          if (data.fan == true) {
            fanImg.src = "../static/FanOn.png";
            fanImg.classList.add("spin_animation");
          } else {
            fanImg.src = "../static/FanOff.png";
            fanImg.classList.remove("spin_animation");
          }
        }*/
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
      const imgElement = document.getElementById('th_img_n');
      const notifElement = document.getElementById('thspannotif');
      
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
  
    const fanImg = document.getElementById('fanIcon');
  
    /*if (fanImg) {
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
    }*/

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
  
    // Initialize Chart.js
    function initializeChart() {
      if (typeof Chart !== 'undefined') {
        const chart = new Chart("myChart", {
          type: "line",
          data: {
            labels: xValues,
            datasets: [{ 
              label: 'Temperature Data',
              data: temperature_data,
              lineTension: 0,
              borderColor: "red",
              fill: false,
            }, {
              label: 'Humidity Data',
              data: humidity_data,
              lineTension: 0,
              borderColor: "blue",
              fill: false,
            }, {
              label: 'Temperature Threshold',
              data: temp_treshold,
              lineTension: 0,
              borderColor: "pink",
              fill: false,
              pointStyle: "line"
            }, { 
              label: 'Humidity Threshold',
              data: hum_treshold,
              lineTension: 0,
              borderColor: "violet",
              fill: false,
              pointStyle: "line"
            }]
          },
          options: {
            legend: {display: true},
            animation: false
          }
        });
        
        // Set global default font color
        Chart.defaults.global.defaultFontColor = "#fff";
        
        return chart;
      } else {
        console.error("Chart.js not loaded");
        return null;
      }
    }
  
    let newX = 0;
    let chart = null;
  
    function setThreshold(TT, HT) {
      temp_treshold.splice(0);
      hum_treshold.splice(0);
      for (let i = 0; i < 13; i++) {
        temp_treshold.push(23);
        hum_treshold.push(15);
      }
    }
  
    function newData(CurrentTemperature = 0, CurrentHumidity = 0) {
      if (newX >= 13) {
        let lastData = xValues[xValues.length - 1];
        xValues.shift();     
        //newX -= 50;
      } else {
        newX++;
      }
      
      let now = new Date();
      let hours = now.getHours();
      let minutes = now.getMinutes();
      let seconds = now.getSeconds();
      xValues.push(`${hours}:${minutes}:${seconds}|`);
      
      if (temperature_data.length >= 13 && humidity_data.length >= 13) {
        temperature_data.shift();
        humidity_data.shift();
      }
      
      temperature_data.push({x: newX/10, y: CurrentTemperature});
      humidity_data.push({x: newX/10, y: CurrentHumidity});
      
      if (chart) {
        chart.update("none");
      }
    }
  
    function logData() {
      console.log("Light intensity:", last_Light);
      const ledStatusElement = document.getElementById("led-status");
      console.log("LED Status:", ledStatusElement ? ledStatusElement.textContent : "unknown");
      console.log("Threshold", lightThreshold);
    }
  
    // Update function to call both data updates
    function updateAllData() {
      updateHumTemp();
      updateLightData();
      updateRFIDData();
      updateProfile();
      logData();
    }
  
    // Initialize everything when the page is loaded
    function initializeApp() {
      setThreshold();
      loadBars();
      chart = initializeChart();
      
      // Initial data loading
      updateRFIDData().then(() => {
        console.log("Initial RFID data loaded");
      }).catch(error => {
        console.error("Error loading initial RFID data:", error);
      });
      
      // Fix for profile images
      const profileImages = document.querySelectorAll('.profile-img');
      profileImages.forEach(img => {
        if (!img.getAttribute('src')) {
          img.src = 'https://via.placeholder.com/150/CCCCCC/FFFFFF?text=No+Profile';
        }
      });
      
      // Start periodic updates
      setInterval(updateAllData, 1000);
    }
  
    // Initialize the application
    initializeApp();
  });