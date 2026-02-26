import { useEffect, useMemo, useState } from 'react';
import { io } from 'socket.io-client';
import { fetchBattery, getApiBaseUrl } from '../data/backendApi';

interface LiveBatteryState {
  battery: number | null;
  isConnected: boolean;
}

export function useLiveBattery(): LiveBatteryState {
  const [battery, setBattery] = useState<number | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

  useEffect(() => {
    let isMounted = true;

    const socketUrl = apiBaseUrl || undefined;

    const socket = io(socketUrl, {
      path: '/socket.io',
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
      setBattery(typeof data?.battery === 'number' ? data.battery : null);
    });

    fetchBattery()
      .then((data) => {
        if (!isMounted) {
          return;
        }
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
