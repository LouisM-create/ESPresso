const client = mqtt.connect("ws://hellgate.ddns.net:8083");

let heizungStatus = "off"; // Startzustand der Heizung

client.on("connect", () => {
    console.log("[MQTT] Verbunden mit Broker!");
    client.subscribe("esp8266/heizungStatus");
});
client.on('message', (topic, message) => {
    if (topic === 'esp8266/heizungStatus') {
        let button = document.getElementById("heizungButton");
        let text = document.getElementById("buttonText");

        if (message.toString() === "On") {
            button.style.backgroundColor = "green"; // Grün für An
            text.innerText = "An";
            heizungStatus = "on";

        } else if (message.toString() === "Off") {
            button.style.backgroundColor = "red"; // Rot für Aus
            text.innerText = "Aus";
            heizungStatus = "off";

        } else if (message.toString() === "Auto") {
            button.style.backgroundColor = "orange"; // Orange für Automatik
            text.innerText = "Automatik";
            heizungStatus = "auto";

        } else {
            console.error("Unbekannter Heizungsstatus:", message.toString());
        }	
    }
});


function toggleHeizung() {

    // Zustand wechseln: off -> on -> auto -> off ...
    if (heizungStatus === "off") {
        fetch("heizung/on", { method: "POST" })
            .then(res => res.json())
            .then(data => {
            console.log(data);
        })
    } else if (heizungStatus === "on") {
        fetch("heizung/off", { method: "POST" })
            .then(res => res.json())
            .then(data => {
                console.log(data);
            });
        
    } else if (heizungStatus === "auto") {
        fetch("heizung/auto", { method: "POST" })
            .then(res => res.json())
            .then(data => {
                console.log(data);
            });
       
    } else {
        console.error("Unbekannter Heizungsstatus:", heizungStatus);
    }
}
