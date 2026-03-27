import { useEffect, useMemo, useState } from 'react';
import { io } from 'socket.io-client';
import { getApiBaseUrl } from '../data/backendApi';
import type { Tag } from '../types';

interface BatteryUpdateEvent {
  tagId?: number;
  batteryPct?: number | null;
  status?: Tag['status'];
}

interface LiveTagsState {
  tags: Tag[];
  isConnected: boolean;
  lastBatteryUpdate: { tagId: number; batteryPct: number } | null;
}

export function useLiveTags(initialTags: Tag[] | undefined): LiveTagsState {
  const [tags, setTags] = useState<Tag[]>(initialTags ?? []);
  const [isConnected, setIsConnected] = useState(false);
  const [lastBatteryUpdate, setLastBatteryUpdate] = useState<{ tagId: number; batteryPct: number } | null>(null);

  const apiBaseUrl = useMemo(() => getApiBaseUrl(), []);

  useEffect(() => {
    setTags(initialTags ?? []);
  }, [initialTags]);

  useEffect(() => {
    const socketUrl = apiBaseUrl || undefined;
    const socket = io(socketUrl, {
      path: '/socket.io',
      transports: ['polling'],
      reconnection: true,
    });

    socket.on('connect', () => {
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.on('battery_update', (data: BatteryUpdateEvent) => {
      if (!Number.isInteger(data?.tagId) || typeof data?.batteryPct !== 'number') {
        return;
      }

      const nextTagId = data.tagId;
      const nextBatteryPct = data.batteryPct;

      setTags((currentTags) =>
        currentTags.map((tag) =>
          tag.id === nextTagId
            ? {
                ...tag,
                batteryPct: nextBatteryPct,
                status: data.status ?? tag.status,
              }
            : tag
        )
      );
      setLastBatteryUpdate({ tagId: nextTagId, batteryPct: nextBatteryPct });
    });

    return () => {
      socket.disconnect();
    };
  }, [apiBaseUrl]);

  return { tags, isConnected, lastBatteryUpdate };
}
