import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';
import { AppNotification } from '../types';

interface NotificationBannerProps {
  notification: AppNotification;
  onClose: () => void;
}

export const NotificationBanner: React.FC<NotificationBannerProps> = ({ 
  notification, 
  onClose 
}) => {
  const styles = {
    success: { bg: 'bg-green-100', border: 'border-green-600', icon: CheckCircle, color: 'text-green-600' },
    error: { bg: 'bg-red-100', border: 'border-red-600', icon: AlertCircle, color: 'text-red-600' },
    info: { bg: 'bg-blue-100', border: 'border-blue-600', icon: AlertCircle, color: 'text-blue-600' },
  };

  const style = styles[notification.type];
  const Icon = style.icon;

  return (
    <div className={`p-4 border-2 ${style.border} ${style.bg}`}>
      <div className="flex items-center gap-2">
        <Icon className={`w-5 h-5 ${style.color}`} />
        <span className="font-semibold flex-1">{notification.message}</span>
        <button onClick={onClose} className="text-gray-600 hover:text-black font-bold text-xl">
          ×
        </button>
      </div>
    </div>
  );
};