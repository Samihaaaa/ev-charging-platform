const API_URL = "http://127.0.0.1:8001";

export const api = {
  getHeaders: () => {
    const token = localStorage.getItem("token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  },

  async login(email, password) {
    console.log("Login request sent");
    console.log("Calling login API:", `${API_URL}/auth/login`);
    console.log("Email being sent:", email);
    console.log("Password being sent:", password);
    
    // Backend expects form data, not JSON
    const formData = new URLSearchParams();
    formData.append("username", email); // OAuth2PasswordRequestForm uses 'username' field
    formData.append("password", password);
    
    console.log("Form data being sent:");
    console.log("Username field:", formData.get("username"));
    console.log("Password field:", formData.get("password"));
    console.log("Form data string:", formData.toString());
    
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: formData
    });
    
    console.log("Login response status:", res.status);
    console.log("Login response OK:", res.ok);
    
    if (!res.ok) {
      let data = {};
      try {
        data = await res.json();
      } catch {
        data = {};
      }
      
      console.error("Login error:", data);
      
      const message =
        typeof data === "string"
          ? data
          : data?.detail
          ? data.detail
          : JSON.stringify(data);
      
      throw new Error(message);
    }
    
    const data = await res.json();
    console.log("Login response:", data);
    return data;
  },

  async register(email, password) {
    console.log("Registration request sent");
    console.log("Calling registration API:", `${API_URL}/users/`);
    console.log("Email being sent:", email);
    console.log("Password being sent:", password);
    console.log("Request body:", JSON.stringify({ email, password }));
    
    const res = await fetch(`${API_URL}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    
    console.log("Registration response status:", res.status);
    console.log("Registration response OK:", res.ok);
    
    if (!res.ok) {
      const err = await res.json();
      console.error("Registration error:", err);
      throw new Error(err.detail || "Registration failed");
    }
    
    const data = await res.json();
    console.log("Registration response:", data);
    return data;
  },

  async getStations() {
    const res = await fetch(`${API_URL}/stations/`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load stations");
    return res.json();
  },

  async getAvailableSlots(stationId) {
    const res = await fetch(`${API_URL}/stations/${stationId}/available-slots`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load slots");
    return res.json();
  },

  async bookSlot(stationId, timeSlot) {
    console.log("Booking slot:", { stationId, timeSlot });
    const res = await fetch(`${API_URL}/payments/checkout-session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }, // No auth headers for demo
      body: JSON.stringify({ station_id: stationId, time_slot: timeSlot }),
    });
    if (!res.ok) {
        const err = await res.json();
        console.error("Booking failed:", err);
        throw new Error(err.detail || err.error || "Booking failed");
    }
    const data = await res.json();
    console.log("Booking response:", data);
    return data;
  },

  async getMyBookings() {
    console.log("Fetching bookings from:", `${API_URL}/bookings/my-bookings/demo`);
    const res = await fetch(`${API_URL}/bookings/my-bookings/demo`, {
      headers: { "Content-Type": "application/json" }, // No auth headers for demo
    });
    if (!res.ok) throw new Error("Failed to load bookings");
    const data = await res.json();
    console.log("Bookings API response:", data);
    return data;
  },

  async cancelBooking(id) {
    const url = `${API_URL}/bookings/${id}/cancel`;
    const token = localStorage.getItem("token");
    console.log("Token:", token);
    console.log("Cancelling booking:", id);
    console.log("Calling DELETE:", url);
    
    const res = await fetch(url, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` })
      }
    });
    
    console.log("Response status:", res.status);
    console.log("Response OK:", res.ok);
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      console.error("Cancel booking error:", errorData);
      throw new Error(errorData.detail || `Failed to cancel booking (${res.status})`);
    }
    
    const data = await res.json();
    console.log("Cancel booking response:", data);
    return data;
  }
};
