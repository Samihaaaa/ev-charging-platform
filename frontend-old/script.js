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

<h3>?? ${station.name}</h3>

<p>Type: ${station.charger_type}</p>

<p>Power: <b>${station.power_kw} kW</b></p>

<p>Price: <b>??${station.price_inr || 500}</b></p>

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

console.log(`Viewing slots for station ${stationId}`);

const res = await fetch(`${API_URL}/stations/${stationId}/available-slots`);

const data = await res.json();

console.log("Available slots response:", data);

const slots = data.available_slots;
const priceInr = data.price_inr || 500; // Default to 500 INR if not specified

const slotDiv = document.getElementById(`slots-${stationId}`);

slotDiv.innerHTML = "";

if (!slots || slots.length === 0) {

slotDiv.innerHTML = "<p>No slots available</p>";
return;

}

slots.forEach(slot => {

const btn = document.createElement("button");

btn.innerText = `Book ${slot} - ${priceInr} INR`;

btn.className = "slot-btn";

btn.onclick = () => bookSlot(stationId, slot);

slotDiv.appendChild(btn);

});

console.log(`Displayed ${slots.length} available slots`);

}



/* ================= BOOK SLOT ================= */

async function bookSlot(stationId, slot) {

console.log(`Booking station ${stationId}, slot ${slot}`);

const res = await fetch(`${API_URL}/payments/checkout-session`, {

method: "POST",

headers: {
"Content-Type": "application/json"
},

body: JSON.stringify({
station_id: stationId,
time_slot: slot
})

});

const data = await res.json();

console.log("Booking response:", data);

if (res.ok && data.status === "success") {

alert(`Booking successful! Booking ID: ${data.booking_id}`);

// Refresh stations to update available slots
loadStations();

// Refresh bookings to show new booking
loadMyBookings();

} else {

alert(data.error || data.detail || "Booking failed");

}

}



/* ================= LOAD MY BOOKINGS ================= */

async function loadMyBookings() {

console.log("Loading my bookings...");

const res = await fetch(`${API_URL}/bookings/my-bookings/demo`);

const bookings = await res.json();

console.log("Bookings response:", bookings);

const container = document.getElementById("bookings");

container.innerHTML = "";

if (!bookings || bookings.length === 0) {

container.innerHTML = "<p>No Active Bookings</p>";
return;

}

bookings.forEach(b => {

const div = document.createElement("div");

div.className = "booking-card";

div.innerHTML = `

<b>Station:</b> ${b.station_name || 'Station ' + b.station_id}
<br>

<b>Time Slot:</b> ${b.time_slot}
<br>

<b>Status:</b> ${b.status || 'confirmed'}

<br><br>

<button onclick="cancelBooking(${b.id})">
Cancel Booking
</button>

`;

container.appendChild(div);

});

console.log(`Displayed ${bookings.length} bookings`);

}



/* ================= CANCEL BOOKING ================= */

async function cancelBooking(id) {

console.log(`Cancelling booking ${id}`);

const res = await fetch(`${API_URL}/bookings/${id}`, {

method: "DELETE"

});

const data = await res.json();

console.log("Cancel response:", data);

if (res.ok && data.status === "success") {

alert(`Booking cancelled! Slot ${data.slot_freed} is now available.`);

// Refresh bookings to remove cancelled booking
loadMyBookings();

// Refresh stations to show freed slot
loadStations();

} else {

alert(data.detail || "Failed to cancel booking");

}

}



/* ================= AUTO LOAD ================= */

loadStations();
loadMyBookings();

function logout(){

localStorage.removeItem("token")

window.location.href="login.html"

}