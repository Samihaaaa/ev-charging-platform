const API_URL = "http://127.0.0.1:8001";

let token = localStorage.getItem("token");



/* ================= REGISTER ================= */

const registerForm = document.getElementById("registerForm");

if (registerForm) {

registerForm.addEventListener("submit", async (e) => {

e.preventDefault();

const email = document.getElementById("regEmail").value;
const password = document.getElementById("regPassword").value;

const res = await fetch(`${API_URL}/users/`, {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({
email: email,
password: password
})
});

if (res.ok) {

alert("User registered successfully!");
window.location.href = "login.html";

} else {

const err = await res.json();
alert("Error: " + JSON.stringify(err));

}

});

}



/* ================= LOGIN ================= */

const loginForm = document.getElementById("loginForm");

if (loginForm) {

loginForm.addEventListener("submit", async (e) => {

e.preventDefault();

const email = document.getElementById("email").value;
const password = document.getElementById("password").value;

const formData = new URLSearchParams();

formData.append("username", email);
formData.append("password", password);

const res = await fetch(`${API_URL}/auth/login`, {
method: "POST",
body: formData
});

if (!res.ok) {

alert("Login failed");
return;

}

const data = await res.json();

localStorage.setItem("token", data.access_token);

window.location.href = "dashboard.html";

});

}



/* ================= LOAD STATIONS ================= */

async function loadStations() {

const res = await fetch(`${API_URL}/stations/`);
const stations = await res.json();

const container = document.getElementById("stations");

container.innerHTML = "";

stations.forEach(station => {

const card = document.createElement("div");
card.className = "card";

card.innerHTML = `

<h3>⚡ ${station.name}</h3>

<p>Type: ${station.charger_type}</p>

<p>Power: <b>${station.power_kw} kW</b></p>

<button onclick="viewSlots(${station.id})">
View Available Slots
</button>

<div id="slots-${station.id}" class="slots"></div>

`;

container.appendChild(card);

});

}



/* ================= VIEW AVAILABLE SLOTS ================= */

async function viewSlots(stationId) {

const res = await fetch(`${API_URL}/stations/${stationId}/available-slots`);

const data = await res.json();

const slots = data.available_slots;

const slotDiv = document.getElementById(`slots-${stationId}`);

slotDiv.innerHTML = "";

if (!slots || slots.length === 0) {

slotDiv.innerHTML = "<p>No slots available</p>";
return;

}

slots.forEach(slot => {

const btn = document.createElement("button");

btn.innerText = `Book ${slot}`;

btn.className = "slot-btn";

btn.onclick = () => bookSlot(stationId, slot);

slotDiv.appendChild(btn);

});

}



/* ================= BOOK SLOT ================= */

async function bookSlot(stationId, slot) {

if (!token) {

alert("Please login first");
window.location.href = "login.html";
return;

}

const res = await fetch(`${API_URL}/bookings/`, {

method: "POST",

headers: {
"Content-Type": "application/json",
"Authorization": "Bearer " + token
},

body: JSON.stringify({
station_id: stationId,
time_slot: slot
})

});

const data = await res.json();

if (res.ok) {

alert("Booking successful!");

loadStations();
loadMyBookings();

} else {

alert(data.detail || "Booking failed");

}

}



/* ================= LOAD MY BOOKINGS ================= */

async function loadMyBookings() {

if (!token) return;

const res = await fetch(`${API_URL}/bookings/my-bookings`, {

headers: {
"Authorization": "Bearer " + token
}

});

const bookings = await res.json();

const container = document.getElementById("bookings");

container.innerHTML = "";

bookings.forEach(b => {

const div = document.createElement("div");

div.className = "booking-card";

div.innerHTML = `

<b>Station ID:</b> ${b.station_id}
<br>

<b>Time Slot:</b> ${b.time_slot}

<br><br>

<button onclick="cancelBooking(${b.id})">
Cancel Booking
</button>

`;

container.appendChild(div);

});

}



/* ================= CANCEL BOOKING ================= */

async function cancelBooking(id) {

await fetch(`${API_URL}/bookings/${id}`, {

method: "DELETE",

headers: {
"Authorization": "Bearer " + token
}

});

alert("Booking cancelled");

loadMyBookings();

}



/* ================= AUTO LOAD ================= */

loadStations();
loadMyBookings();

function logout(){

localStorage.removeItem("token")

window.location.href="login.html"

}