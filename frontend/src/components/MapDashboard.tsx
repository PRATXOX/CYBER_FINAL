'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { AlertTriangle, Activity, MapPin } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom Hotspot Marker Icon
const hotspotIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Custom Normal Marker Icon
const normalIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


type PredictionData = {
  timestamp: string;
  gis_dashboard_data: {
    predicted_hotspots: Array<{
      location_name: string;
      coordinates: { lat: number; lon: number };
      prediction_15_45_min: {
        jam_probability: number;
        is_level_5_hotspot: boolean;
      };
      visual_validation: {
        cause: string;
        exact_density: number;
        thumbnail_url: string;
      };
    }>;
  };
};

export default function MapDashboard() {
  const [data, setData] = useState<PredictionData | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Poll the API every 10 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('https://cyber-final-4cr7.onrender.com/api/predictions');
        if (!res.ok) throw new Error('Network response was not ok');
        const json = await res.json();
        setData(json);
        setLastUpdated(new Date());
      } catch (error) {
        console.error('Error fetching prediction data:', error);
      }
    };

    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 10000); // 10 seconds
    return () => clearInterval(interval);
  }, []);

  const center: [number, number] = [28.6139, 77.2090]; // Default to Delhi

  return (
    <div className="relative h-screen w-full bg-[#0d0d0d]">
      {/* Tactical Header Overlay */}
      <div className="absolute top-4 left-4 z-[1000] rounded-lg border border-gray-800 bg-black/80 p-4 shadow-2xl backdrop-blur-md">
        <h1 className="flex items-center space-x-2 text-xl font-bold tracking-wider text-green-500">
          <Activity className="h-6 w-6" />
          <span>GIS COMMAND CENTER</span>
        </h1>
        <div className="mt-2 text-sm text-gray-400">
          <p>SYSTEM STATUS: <span className="text-green-400">ONLINE</span></p>
          <p>LAST UPDATE: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'AWAITING DATA...'}</p>
        </div>
      </div>

      <MapContainer
        center={center}
        zoom={11}
        className="h-full w-full z-0"
        zoomControl={false}
      >
        {/* CartoDB Dark Matter Tile Layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {data?.gis_dashboard_data.predicted_hotspots.map((hotspot, idx) => {
          const isHotspot = hotspot.prediction_15_45_min.is_level_5_hotspot;
          const probPercentage = (hotspot.prediction_15_45_min.jam_probability * 100).toFixed(1);

          return (
            <Marker
              key={idx}
              position={[hotspot.coordinates.lat, hotspot.coordinates.lon]}
              icon={isHotspot ? hotspotIcon : normalIcon}
            >
              <Popup className="tactical-popup">
                <div className="w-64 rounded bg-gray-900 p-1 text-white">
                  <div className="mb-2 flex items-center justify-between border-b border-gray-700 pb-2">
                    <h3 className="font-bold flex items-center gap-1 text-sm text-gray-100">
                      <MapPin className="h-4 w-4 text-blue-400" />
                      {hotspot.location_name}
                    </h3>
                    {isHotspot && (
                      <span className="flex items-center space-x-1 rounded bg-red-900/50 px-2 py-0.5 text-xs font-semibold text-red-400 border border-red-800">
                        <AlertTriangle className="h-3 w-3" />
                        <span>HOTSPOT</span>
                      </span>
                    )}
                  </div>

                  <div className="relative mb-3 overflow-hidden rounded border border-gray-700">
                    <img
                      src={hotspot.visual_validation.thumbnail_url}
                      alt="CCTV Feed"
                      className="h-24 w-full object-cover opacity-80"
                      onError={(e) => {
                        e.currentTarget.src = "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?q=80&w=400&auto=format&fit=crop";
                      }}
                    />
                    <div className="absolute bottom-1 right-1 rounded bg-black/70 px-1 text-[10px] text-green-400">
                      LIVE FEED
                    </div>
                  </div>

                  <div className="space-y-1.5 text-xs text-gray-300">
                    <div className="flex justify-between">
                      <span className="text-gray-500">DETECTED CAUSE:</span>
                      <span className="font-medium uppercase text-gray-100">{hotspot.visual_validation.cause}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">EXACT DENSITY:</span>
                      <span className="font-medium text-gray-100">{hotspot.visual_validation.exact_density} veh</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">JAM PROBABILITY:</span>
                      <span className={`font-bold ${isHotspot ? 'text-red-400' : 'text-blue-400'}`}>
                        {probPercentage}%
                      </span>
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
