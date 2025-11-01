import { useState, useCallback } from 'react';
import { AppNotification } from '../types';

export function useNotifications() {
  const [notification, setNotification] = useState<AppNotification | null>(null);

  const showNotification = useCallback((type: AppNotification['type'], message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  }, []);

  const clearNotification = useCallback(() => {
    setNotification(null);
  }, []);

  return { notification, showNotification, clearNotification };
}