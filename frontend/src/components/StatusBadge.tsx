import { Clock, RefreshCw, CheckCircle, AlertCircle } from "lucide-react";
import { Call } from "../types";

export const StatusBadge: React.FC<{ status: Call['status'] }> = ({ status }) => {
    const styles = {
      pending: { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100', border: 'border-yellow-600' },
      in_progress: { icon: RefreshCw, color: 'text-blue-600', bg: 'bg-blue-100', border: 'border-blue-600' },
      completed: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100', border: 'border-green-600' },
      failed: { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-100', border: 'border-red-600' },
    };
  
    const style = styles[status];
    const Icon = style.icon;
  
    return (
      <div className={`flex items-center gap-2 px-3 py-1 border-2 ${style.border} ${style.bg}`}>
        <Icon className={`w-4 h-4 ${style.color} ${status === 'in_progress' ? 'animate-spin' : ''}`} />
        <span className={`font-semibold ${style.color} uppercase text-sm`}>
          {status.replace('_', ' ')}
        </span>
      </div>
    );
  };