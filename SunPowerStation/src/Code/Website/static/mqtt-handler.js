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
        temperaturDiv.innerText = message.toString(); // Kein HTML, nur Text
    }
});


// Grafik

document.addEventListener("DOMContentLoaded", function() {
    const ctx = document.getElementById("temperatureChart").getContext("2d");

    let temperatureChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Temperaturverlauf",
                data: [],
                borderColor: "red",
                backgroundColor: "rgba(255, 0, 0, 0.2)",
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: "Uhrzeit" } },
                y: { 
                    title: { display: true, text: "Temperatur (°C)" },
                    ticks: {
                        callback: function(value) {
                            if (value === 20) {
                                return "🔵 " + value;  // Blau für 15°C
                            } else if (value === 30) {
                                return "🔴 " + value;  // Rot für 40°C
                            }
                            return value;  // Standardfarbe für andere Zahlen
                        }
                    }
                }
            },
            plugins: {
                annotation: {
                    annotations: {
                        minLine: {
                            type: "line",
                            yMin: 15,
                            yMax: 15,
                            borderColor: "blue",
                            borderWidth: 2,
                            label: {
                                enabled: true,
                                content: "Min-Wert",
                                position: "start"
                            }
                        },
                        maxLine: {
                            type: "line",
                            yMin: 40,
                            yMax: 40,
                            borderColor: "orange",
                            borderWidth: 2,
                            label: {
                                enabled: true,
                                content: "Max-Wert",
                                position: "start"
                            }
                        }
                    }
                }
            }
        }
    });

    function fetchTemperatureData() {
        fetch("/temperature-data")
            .then(response => response.json())
            .then(data => {
                let labels = data.map(entry => entry.zeit);
                let temperatures = data.map(entry => entry.temperatur);

                temperatureChart.data.labels = labels;
                temperatureChart.data.datasets[0].data = temperatures;
                temperatureChart.update();
            })
            .catch(error => console.error("Fehler beim Laden der Temperaturdaten:", error));
    }

    // Temperaturdaten abrufen und alle 10 Sekunden aktualisieren
    fetchTemperatureData();
    setInterval(fetchTemperatureData, 10000);
});
