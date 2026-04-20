'use client';

import dynamic from 'next/dynamic';

// Dynamically import MapDashboard to prevent SSR issues with Leaflet
const MapDashboard = dynamic(() => import('./MapDashboard'), {
  ssr: false,
  loading: () => (
    <div className="flex h-screen w-full items-center justify-center bg-[#0d0d0d] text-green-500 font-mono">
      <div className="flex flex-col items-center space-y-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-green-500 border-t-transparent"></div>
        <p className="animate-pulse tracking-widest text-lg">INITIALIZING TACTICAL GIS NETWORK...</p>
      </div>
    </div>
  ),
});

export default function MapLoader() {
  return <MapDashboard />;
}
