const client = mqtt.connect("ws://hellgate.ddns.net:8083");

client.on('connect', () => {
    console.log("Verbunden");
    client.subscribe("esp8266/temperature/ack");
});

// Status Anzeige
let statusDiv = document.querySelector('.status');
let statusText = document.querySelector('.statusText p');
let timeoutHandle = null;

function setConnectedStatus() {
    statusDiv.classList.add('connected');
    statusText.textContent = "ESP8266 is connected";

    if (timeoutHandle) clearTimeout(timeoutHandle);

    timeoutHandle = setTimeout(() => {
        statusDiv.classList.remove('connected');
        statusText.textContent = "!! ESP8266 is not connected !!";
    }, 12000);
}

// Nur ein einziger message-Handler!
client.on('message', (topic, message) => {
    if (topic === 'esp8266/temperature/ack') {
        setConnectedStatus();

        const temperaturDiv = document.getElementById('aktuelleTemperatur');
        const now = new Date().toLocaleTimeString();
        temperaturDiv.innerHTML = `Aktuell:<br>${message.toString()}°C<br>${now} Uhr`;
    }
});
