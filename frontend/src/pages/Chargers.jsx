import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { MapPin, Zap, Search, DollarSign, Navigation } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Chargers = () => {
  const [chargers, setChargers] = useState([]);
  const [filteredChargers, setFilteredChargers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [activeStationId, setActiveStationId] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [allSlots, setAllSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();
  const { token } = useAuth();

  useEffect(() => {
    const fetchStations = async () => {
      try {
        const data = await api.getStations();
        setChargers(data);
        setFilteredChargers(data);
      } catch (err) {
        console.error("Failed to load stations", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStations();
  }, []);

  // Listen for booking cancellation events to refresh slots
  useEffect(() => {
    const handleBookingCancelled = (event) => {
      console.log("Booking cancelled event received:", event.detail);
      
      // If we have an active station, refresh its slots
      if (activeStationId) {
        console.log("Refreshing slots for active station:", activeStationId);
        handleViewSlots(activeStationId);
      }
    };

    window.addEventListener('bookingCancelled', handleBookingCancelled);
    
    return () => {
      window.removeEventListener('bookingCancelled', handleBookingCancelled);
    };
  }, [activeStationId]);

  useEffect(() => {
    let result = chargers;
    if (searchTerm) {
      result = result.filter(c => c.name.toLowerCase().includes(searchTerm.toLowerCase()));
    }
    if (filterType !== 'all') {
      result = result.filter(c => c.charger_type && c.charger_type.toLowerCase() === filterType.toLowerCase());
    }
    setFilteredChargers(result);
  }, [searchTerm, filterType, chargers]);

  const handleViewSlots = async (id) => {
    console.log("Viewing slots for station:", id);
    
    if (activeStationId === id) {
      setActiveStationId(null);
      return;
    }
    
    setActiveStationId(id);
    setLoadingSlots(true);
    try {
      const data = await api.getAvailableSlots(id);
      console.log("Available slots response:", data);
      setAvailableSlots(data.available_slots || []);
      setAllSlots(data.all_slots || [
        "9am-10am", "10am-11am", "11am-12pm", 
        "12pm-1pm", "1pm-2pm", "2pm-3pm", 
        "3pm-4pm", "4pm-5pm", "5pm-6pm"
      ]);
    } catch (err) {
      console.error("Failed to load slots:", err);
      setAvailableSlots([]);
      setAllSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleBook = async (stationId, slot) => {
    console.log("Booking slot:", { stationId, slot });
    try {
      const data = await api.bookSlot(stationId, slot);
      console.log("Booking response:", data);
      
      if (data.status === "success") {
        setSuccessMessage(`Booking successful! Booking ID: ${data.booking_id}`);
        
        // Refresh available slots for this station
        try {
          const slotsData = await api.getAvailableSlots(stationId);
          setAvailableSlots(slotsData.available_slots || []);
        } catch (e) {
          console.error("Failed to refresh slots:", e);
        }

        // Navigate to bookings page after a short delay
        setTimeout(() => {
          navigate('/bookings');
        }, 2000);
      } else {
        alert(data.error || data.detail || "Booking failed");
      }
    } catch (err) {
      console.error("Booking error:", err);
      alert("Booking failed: " + err.message);
    }
  };

  if (loading) return <div>Loading chargers...</div>;

  return (
    <div>
      {successMessage && (
        <div style={{ padding: '1rem', marginBottom: '1.5rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.2)', display: 'flex', alignItems: 'center', gap: '0.8rem', animation: 'fadeIn 0.3s ease-out' }}>
          <div style={{ width: '24px', height: '24px', backgroundColor: 'var(--success)', borderRadius: '50%', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
          </div>
          <span style={{ fontWeight: 500, fontSize: '0.95rem' }}>{successMessage}</span>
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <h1 className="page-title" style={{ margin: 0 }}>Discover Chargers</h1>
        
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', width: '250px' }}>
            <Search size={18} style={{ position: 'absolute', top: '50%', transform: 'translateY(-50%)', left: '1rem', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              className="input-control" 
              placeholder="Search by name..." 
              style={{ paddingLeft: '2.5rem', marginBottom: 0 }}
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>
          <select 
            className="input-control" 
            style={{ marginBottom: 0, width: '150px' }}
            value={filterType}
            onChange={e => setFilterType(e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="fast">Fast</option>
            <option value="standard">Standard</option>
          </select>
        </div>
      </div>

      <div className="chargers-grid">
        {filteredChargers.map(charger => (
          <div key={charger.id} className="card charger-card">
            <h3><Zap size={20} color="var(--primary)" /> {charger.name}</h3>
            
            <div className="badges-container">
              <span className="badge fast">{charger.charger_type || 'Standard'}</span>
              <span className="badge">₹{charger.price_inr || 500}/hr</span>
              <span className="badge" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary)' }}>{charger.power_kw} kW</span>
            </div>

            <div className="info-row" style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
              <span className="info-label"><MapPin size={16} style={{ display: 'inline', verticalAlign: 'middle' }} /> Location</span>
              <span className="info-value">Station #{charger.id}</span>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
              <button 
                className="btn-primary" 
                style={{ flex: 1 }}
                onClick={() => handleViewSlots(charger.id)}
              >
                {activeStationId === charger.id ? 'Hide Slots' : 'View Slots'}
              </button>
              
              <button 
                className="btn-outline" 
                style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}
                onClick={() => {
                  const lat = charger.latitude || 12.9716;
                  const lng = charger.longitude || 77.5946;
                  window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`, '_blank', 'noopener,noreferrer');
                }}
                title="Get Directions"
              >
                <Navigation size={16} /> Directions
              </button>
            </div>

            {activeStationId === charger.id && (
              <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                {loadingSlots ? (
                  <div style={{ textAlign: 'center', fontSize: '0.9rem' }}>Checking slots...</div>
                ) : allSlots.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {allSlots.map(slot => {
                      const isAvailable = availableSlots.includes(slot);
                      return (
                        <button 
                          key={slot} 
                          disabled={!isAvailable}
                          className="btn-outline" 
                          style={{ 
                            padding: '0.5rem 0.8rem', 
                            fontSize: '0.85rem',
                            opacity: isAvailable ? 1 : 0.5,
                            cursor: isAvailable ? 'pointer' : 'not-allowed',
                            textDecoration: isAvailable ? 'none' : 'line-through',
                            backgroundColor: isAvailable ? 'transparent' : 'rgba(0,0,0,0.05)',
                            borderColor: isAvailable ? 'var(--primary)' : 'var(--border-color)'
                          }}
                          onClick={() => handleBook(charger.id, slot)}
                          title={isAvailable ? `Book ${slot}` : "Slot Booked"}
                        >
                          {slot}
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', fontSize: '0.9rem', color: 'var(--danger)' }}>No slots fetched.</div>
                )}
              </div>
            )}
          </div>
        ))}
        {filteredChargers.length === 0 && (
          <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            No chargers found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
};

export default Chargers;
