const client = mqtt.connect("ws://hellgate.ddns.net:8083");

client.on("connect", () => {
    console.log("[MQTT] Verbunden mit Broker!");
});

let heizungStatus = "off"; // Startzustand der Heizung

function toggleHeizung() {
    let button = document.getElementById("heizungButton");
    let text = document.getElementById("buttonText");

    // Zustand wechseln: off -> on -> auto -> off ...
    if (heizungStatus === "off") {
        heizungStatus = "on";
        client.publish("esp8266/heizung", "on"); // MQTT-Nachricht senden
        button.style.backgroundColor = "green"; // Grün für An
        text.innerText = "An";
    } else if (heizungStatus === "on") {
        heizungStatus = "auto";
        client.publish("esp8266/heizung", "auto"); // MQTT-Nachricht senden
        button.style.backgroundColor = "orange"; // Orange für Automatik
        text.innerText = "Automatik";
    } else {
        heizungStatus = "off";
        client.publish("esp8266/heizung", "off"); // MQTT-Nachricht senden
        button.style.backgroundColor = "#888888"; // Grau für Aus
        text.innerText = "Aus";
    }
}
