// Standard-Funktionen (Navigation und Steuerung)
console.log("Hello World");

function redirect() {
    window.location.href = "/test";
}

function buttonClicked1() {
    window.location.href = "/temperatur";
}

function buttonClicked2() {
    window.location.href = "/heizung";
}   

function homeButoon() {
    window.location.href = "/";
}

function heizungAn() {
    alert("Heizung wurde eingeschaltet");
}

function heizungAus() {
    alert("Heizung wurde ausgeschaltet");
}

function automatikBetrieb() {
    alert("Heizung wurde auf Automatik gestellt");
}

function steuerung() {
    window.location.href = "/steuerung";
}