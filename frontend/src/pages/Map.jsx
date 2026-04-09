import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';

const MapView = () => {
  const [chargers, setChargers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStations = async () => {
      try {
        const data = await api.getStations();
        setChargers(data);
      } catch (err) {
        console.error("Failed to load stations", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStations();
  }, []);

  if (loading) return <div>Loading map...</div>;

  // Default center (Bangalore)
  const defaultCenter = [12.9716, 77.5946];

  return (
    <div>
      <h1 className="page-title">Interactive Map</h1>
      <div className="map-container">
        <MapContainer 
          center={chargers[0] && chargers[0].latitude ? [chargers[0].latitude, chargers[0].longitude] : defaultCenter} 
          zoom={12} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {chargers.map(charger => {
            // Provide fallback coordinates for testing if backend lacks lat/lon
            const lat = charger.latitude || (defaultCenter[0] + (Math.random() - 0.5) * 0.1);
            const lng = charger.longitude || (defaultCenter[1] + (Math.random() - 0.5) * 0.1);

            return (
              <Marker key={charger.id} position={[lat, lng]}>
                <Popup>
                  <h4>⚡ {charger.name}</h4>
                  <p>Type: {charger.charger_type || 'Standard'}</p>
                  <p>Power: <b>{charger.power_kw} kW</b></p>
                  <p>Price: <b>₹{charger.price_inr || 500}</b></p>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <button 
                      className="btn-primary" 
                      style={{ padding: '0.4rem', fontSize: '0.85rem', flex: 1 }}
                      onClick={() => navigate('/chargers')}
                    >
                      View Slots
                    </button>
                    <button 
                      className="btn-outline" 
                      style={{ padding: '0.4rem', fontSize: '0.85rem', flex: 1 }}
                      onClick={() => window.open(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`, '_blank', 'noopener,noreferrer')}
                    >
                      Directions
                    </button>
                  </div>
                </Popup>
              </Marker>
            )
          })}
        </MapContainer>
      </div>
    </div>
  );
};

export default MapView;
