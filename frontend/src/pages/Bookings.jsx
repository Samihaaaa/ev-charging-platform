import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { History, XCircle, MapPin, Zap } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Bookings = () => {
  const [bookings, setBookings] = useState([]);
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);
  const navigate = useNavigate();
  const { token } = useAuth();

  // Function to check if booking can be cancelled (within 30 minutes)
  const canCancelBooking = (booking) => {
    if (!booking.created_at) return true; // If no created_at, allow cancellation
    
    try {
      const createdTime = new Date(booking.created_at);
      const currentTime = new Date();
      const timeDiff = (currentTime - createdTime) / (1000 * 60); // Convert to minutes
      
      // Debug logging
      console.log("Booking created_at:", booking.created_at);
      console.log("Created time:", createdTime);
      console.log("Current time:", currentTime);
      console.log("Time diff (minutes):", timeDiff);
      
      return timeDiff <= 30;
    } catch (error) {
      console.error("Error parsing created_at:", error);
      return true; // If parsing fails, allow cancellation
    }
  };

  // Function to get time remaining for cancellation
  const getCancellationTimeRemaining = (booking) => {
    if (!booking.created_at) return "N/A";
    
    try {
      const createdTime = new Date(booking.created_at);
      const currentTime = new Date();
      const timeDiff = (currentTime - createdTime) / (1000 * 60); // Convert to minutes
      
      if (timeDiff >= 30) return "Expired";
      
      const remainingMinutes = Math.ceil(30 - timeDiff);
      return `${remainingMinutes} min`;
    } catch (error) {
      console.error("Error calculating time remaining:", error);
      return "N/A";
    }
  };

  const fetchBookings = async () => {
    console.log("Bookings page: Fetching bookings...");
    try {
      // Fetch both bookings and stations data
      const [bookingsData, stationsData] = await Promise.all([
        api.getMyBookings(),
        api.getStations()
      ]);
      
      console.log("Bookings page: Received bookings data:", bookingsData);
      console.log("Bookings page: Received stations data:", stationsData);
      
      // Filter only confirmed bookings (exclude cancelled)
      const confirmedBookings = bookingsData.filter(booking => booking.status === "confirmed");
      console.log("Bookings page: Filtered confirmed bookings:", confirmedBookings.length);
      
      setBookings(confirmedBookings);
      setStations(stationsData);
      console.log("Bookings page: State updated with", confirmedBookings.length, "confirmed bookings");
    } catch (err) {
      console.error("Failed to load bookings", err);
      setBookings([]); // Set empty array on error
      setStations([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // For demo mode, fetch data regardless of token
    console.log("Bookings page: Component mounted, fetching data");
    fetchBookings();
  }, []); // Remove token dependency for demo mode

  const handleCancel = async (bookingId) => {
    if (!window.confirm("Are you sure you want to cancel this booking?")) return;
    console.log("Cancelling booking ID:", bookingId);
    setCancellingId(bookingId);
    try {
      // Use API service method
      await api.cancelBooking(bookingId);
      
      alert("Booking cancelled successfully.");
      
      // REMOVE booking instantly from UI
      setBookings(prev => {
        const updated = prev.filter(b => b.id !== bookingId);
        console.log("Updated bookings:", updated);
        return updated;
      });
      
      // REFRESH from backend
      await fetchBookings();
      await api.getStations();
      
    } catch (err) {
      console.error("Cancel booking error:", err);
      const errorMessage = err.response?.data?.detail || err.message;
      
      // Handle specific cancellation window error
      if (errorMessage === "Cancellation window expired") {
        alert("Cannot cancel booking: Cancellation window expired (30-minute limit)");
      } else {
        alert("Failed to cancel booking: " + errorMessage);
      }
    } finally {
      // Reset loading state
      setCancellingId(null);
    }
  };

  // For demo mode, show bookings regardless of token
  if (loading) return <div>Loading bookings...</div>;

  return (
    <div>
      <h1 className="page-title"><History style={{ display: 'inline', verticalAlign: 'middle', marginRight: '0.5rem' }} /> History & Bookings</h1>
      
      {bookings.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <Zap size={48} color="var(--text-muted)" style={{ margin: '0 auto 1rem auto' }} />
          <h3 style={{ marginBottom: '0.5rem' }}>No Active Bookings</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>You don't have any charging sessions scheduled.</p>
          <Link to="/chargers" className="btn-primary">Find a Charger</Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {bookings.filter(b => b.status === "confirmed").map(b => {
            // Find the station to get actual price
            const station = stations.find(s => s.id === b.station_id);
            const actualPrice = station ? station.price_inr : 150;
            const canCancel = canCancelBooking(b);
            const timeRemaining = getCancellationTimeRemaining(b);
            
            return (
            <div key={b.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ padding: '1rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-sm)' }}>
                  <MapPin size={24} color="var(--primary)" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{b.station_name || `Station ${b.station_id}`}</div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Time Slot: <b>{b.time_slot}</b></div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Status: {b.status === 'cancelled' ? 'Cancelled (Refunded)' : (b.status || 'confirmed')}
                    {b.status === 'cancelled' && (
                      <div style={{ color: 'var(--success)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                        Refunded ¥{actualPrice}
                      </div>
                    )}
                  </div>
                  <div style={{ color: 'var(--primary)', fontSize: '0.9rem', fontWeight: 500, marginTop: '0.25rem' }}>
                    <Zap size={14} style={{ display: 'inline', marginRight: '0.25rem' }} />
                    ¥{actualPrice}/hour
                  </div>
                  {b.created_at && (
                    <div style={{ 
                      fontSize: '0.8rem', 
                      marginTop: '0.25rem',
                      color: timeRemaining === "Expired" ? 'var(--danger)' : 'var(--warning)',
                      fontWeight: 500
                    }}>
                      {timeRemaining === "Expired" ? "Cancellation window expired" : `Cancel window: ${timeRemaining} remaining`}
                    </div>
                  )}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span className="badge fast" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>Active</span>
                <button 
                  className="btn-outline" 
                  style={{ 
                    color: canCancel ? 'var(--danger)' : 'var(--text-muted)',
                    borderColor: canCancel ? 'var(--danger)' : 'var(--border-color)',
                    opacity: canCancel ? 1 : 0.5,
                    cursor: canCancel ? 'pointer' : 'not-allowed'
                  }}
                  onClick={() => canCancel && handleCancel(b.id)}
                  disabled={cancellingId === b.id || !canCancel}
                  title={canCancel ? "Cancel booking" : "Cancellation window expired"}
                >
                  {cancellingId === b.id ? 'Cancelling...' : <React.Fragment><XCircle size={16} /> Cancel</React.Fragment>}
                </button>
              </div>
            </div>
          );
        })}
        </div>
      )}
    </div>
  );
};

export default Bookings;
