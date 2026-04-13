import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Zap, MapPin, BatteryCharging, ChevronRight, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { token, user } = useAuth();
  const [stats, setStats] = useState({
    totalChargers: 0,
    activeBookings: 0,
    totalSpent: 0
  });
  const [recentBookings, setRecentBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    console.log("Dashboard: Fetching data...");
    try {
      const [stationsRes, bookingsRes] = await Promise.all([
        api.getStations(),
        api.getMyBookings()
      ]);
      
      console.log("Dashboard: Stations response:", stationsRes);
      console.log("Dashboard: Bookings response:", bookingsRes);
      
      // Filter only confirmed bookings (exclude cancelled)
      const confirmedBookings = bookingsRes.filter(booking => booking.status === "confirmed");
      console.log("Dashboard: Filtered confirmed bookings:", confirmedBookings.length);
      
      // Calculate actual total spent based on station prices
      const totalSpent = confirmedBookings.reduce((sum, booking) => {
        // Find the station for this booking to get actual price
        const station = stationsRes.find(s => s.id === booking.station_id);
        const pricePerHour = station ? station.price_inr : 150; // Default price if station not found
        
        console.log("Dashboard: Booking:", booking);
        console.log("Dashboard: Station found:", station);
        console.log("Dashboard: Price per hour:", pricePerHour);
        console.log("Dashboard: Running total:", sum + pricePerHour);
        
        return sum + pricePerHour;
      }, 0);
      
      const newStats = {
        totalChargers: stationsRes.length,
        activeBookings: confirmedBookings.length,
        totalSpent: totalSpent
      };
      
      console.log("Dashboard: New stats:", newStats);
      setStats(newStats);
      
      const recent = confirmedBookings.slice(0, 3); // Just get 3 most recent confirmed
      console.log("Dashboard: Recent bookings:", recent);
      setRecentBookings(recent);
    } catch (err) {
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // For demo mode, fetch data regardless of token
    console.log("Dashboard: Component mounted, fetching data");
    fetchData();
  }, []); // Remove token dependency for demo mode

  // Listen for stations refresh events
  useEffect(() => {
    const handleStationsRefreshed = (event) => {
      console.log("Dashboard: Stations refresh event received:", event.detail);
      // Refresh dashboard data when stations are updated
      fetchData();
    };

    window.addEventListener('stationsRefreshed', handleStationsRefreshed);
    
    return () => {
      window.removeEventListener('stationsRefreshed', handleStationsRefreshed);
    };
  }, []);

  // Add a refresh function for manual refresh
  const refreshData = () => {
    console.log("Dashboard: Manual refresh triggered");
    setLoading(true);
    fetchData();
  };

  if (loading) return <div>Loading dashboard...</div>;

  return (
    <div>
      <h1 className="page-title">Dashboard Overview</h1>
      
      <div className="dashboard-grid">
        <div className="card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div className="stat-title">Network Status</div>
            <div style={{ padding: '0.4rem', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>
              <Activity size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.totalChargers}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>Active chargers near you</div>
        </div>

        <div className="card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div className="stat-title">Your Bookings</div>
            <div style={{ padding: '0.4rem', borderRadius: '50%', backgroundColor: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary)' }}>
              <BatteryCharging size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.activeBookings}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>Active charging sessions</div>
        </div>

        <div className="card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div className="stat-title">Total Spent</div>
            <div style={{ padding: '0.4rem', borderRadius: '50%', backgroundColor: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' }}>
              <Zap size={20} />
            </div>
          </div>
          <div className="stat-value">₹{stats.totalSpent.toFixed(2)}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>This month</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem' }}>Recent Activity</h3>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button 
                onClick={refreshData}
                style={{ 
                  padding: '0.4rem 0.8rem', 
                  fontSize: '0.75rem', 
                  backgroundColor: 'var(--primary)', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '4px', 
                  cursor: 'pointer' 
                }}
              >
                Refresh
              </button>
              <Link to="/bookings" style={{ color: 'var(--primary)', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                View All <ChevronRight size={16} />
              </Link>
            </div>
          </div>
          
          {recentBookings.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-muted)' }}>
              No recent charging sessions found.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {recentBookings.map((b) => (
                <div key={b.id} style={{ display: 'flex', alignItems: 'center', gap: '1rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: 'var(--bg-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <MapPin size={18} color="var(--primary)" />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600 }}>{b.station_name || `Station ${b.station_id}`}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Slot: {b.time_slot}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Status: {b.status || 'confirmed'}</div>
                  </div>
                  <div className="badge fast">Active</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
