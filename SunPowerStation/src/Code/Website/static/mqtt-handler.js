
//Das ist das skript das die Temperatur auf der html anzeigt
const client = mqtt.connect("ws://hellgate.ddns.net:8083");
    
client.on('connect', () => {
    console.log("Verbunden");
    client.subscribe("esp8266/temperature/ack");
});

client.on('message', (topic, message) => {
    const msgBox = document.getElementById("aktuelleTemperatur");
    msgBox.innerText = message;
});

