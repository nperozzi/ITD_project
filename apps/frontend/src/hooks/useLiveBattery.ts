import { useEffect, useMemo, useState } from 'react';
import { io } from 'socket.io-client';
import { fetchBattery, getApiBaseUrl } from '../data/backendApi';

interface LiveBatteryState {
  battery: number | null;
  isConnected: boolean;
}

export function useLiveBattery(): LiveBatteryState {
  // `battery` is always sourced from backend responses/events (no frontend randomization).
  const [battery, setBattery] = useState<number | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

  useEffect(() => {
    let isMounted = true;

    const socketUrl = apiBaseUrl || undefined;

    const socket = io(socketUrl, {
      path: '/socket.io',
      // Polling avoids websocket upgrade issues with the current backend runtime.
      transports: ['polling'],
      reconnection: true,
    });

    socket.on('connect', () => {
      if (!isMounted) {
        return;
      }
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      if (!isMounted) {
        return;
      }
      setIsConnected(false);
    });

    socket.on('battery_update', (data: { battery?: number | null }) => {
      if (!isMounted) {
        return;
      }
      // Live updates come from backend Socket.IO events.
      setBattery(typeof data?.battery === 'number' ? data.battery : null);
    });

    fetchBattery()
      .then((data) => {
        if (!isMounted) {
          return;
        }
        // Seed UI with latest backend battery value before realtime events arrive.
        setBattery(typeof data.battery === 'number' ? data.battery : null);
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }
        setBattery(null);
      });

    return () => {
      isMounted = false;
      socket.disconnect();
    };
  }, [apiBaseUrl]);

  return { battery, isConnected };
}
