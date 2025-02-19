//by default the switch is off because the switch status is also off if they were to not have the same values, they will act weirdly (OFF for green color, etc)
let ledStatus = 'OFF';

//if button is clicked:
document.getElementById('toggle-button').addEventListener('click', () => {
    // Toggle the switch status. it checks what the status is and does the opposite
    //if its off makes it on
    if (ledStatus === 'OFF') {
        ledStatus = 'ON';
    } 
    //if on make it off
    else {
        ledStatus = 'OFF';
    }            
    //Change the  switch status to whatever the led status is on or off.
    // ex: Switch Status: OFF/ON
    document.getElementById('switch-status').textContent = ledStatus;
    //change the LED COLOR ON SCREEN
    document.getElementById('led').className = ledStatus.toLowerCase();
    
    // Send a request to the Flask backend to update the LED status
    fetch(`/toggle_led?status=${ledStatus}`).then(response => response.json())
        .then(data => {
            console.log(data.message);
        });
});