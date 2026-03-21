import React from 'react';
import { AlertMessage } from '../types';

interface AlertPanelProps {
  alerts: AlertMessage[];
  maxAlerts?: number;
  onClear?: () => void;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({
  alerts,
  maxAlerts = 10,
  onClear,
}) => {
  // 限制显示数量
  const displayAlerts = alerts.slice(0, maxAlerts);
  const hasMore = alerts.length > maxAlerts;
  
  // 获取预警类型颜色
  const getAlertTypeColor = (type: string) => {
    switch (type) {
      case 'proximity':
        return 'bg-yellow-50 border-yellow-400 text-yellow-800';
      case 'triggered':
        return 'bg-red-50 border-red-400 text-red-800';
      case 'resonance':
        return 'bg-green-50 border-green-400 text-green-800';
      default:
        return 'bg-gray-50 border-gray-400 text-gray-800';
    }
  };
  
  const getAlertTypeIcon = (type: string) => {
    switch (type) {
      case 'proximity':
        return '⚡';
      case 'triggered':
        return '🔔';
      case 'resonance':
        return '✨';
      default:
        return 'ℹ️';
    }
  };
  
  const getAlertTypeLabel = (type: string) => {
    switch (type) {
      case 'proximity':
        return '接近预警';
      case 'triggered':
        return '信号触发';
      case 'resonance':
        return '共振预警';
      default:
        return '通知';
    }
  };
  
  if (alerts.length === 0) {
    return (
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <span>实时预警</span>
        </div>
        <div className="text-center text-gray-400 py-8">
          <div className="text-4xl mb-2">📊</div>
          <div>暂无预警</div>
          <div className="text-sm mt-2">
            当价格接近临界点或触发信号时将显示预警
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="card">
      <div className="card-header flex justify-between items-center">
        <span>
          实时预警
          <span className="ml-2 px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
            {alerts.length}
          </span>
        </span>
        {onClear && (
          <button
            onClick={onClear}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            清空
          </button>
        )}
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {displayAlerts.map((alert, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg border-l-4 ${getAlertTypeColor(alert.alert_type)}`}
          >
            <div className="flex items-start">
              <span className="text-xl mr-2">{getAlertTypeIcon(alert.alert_type)}</span>
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-semibold text-sm">{getAlertTypeLabel(alert.alert_type)}</span>
                    <span className="ml-2 text-xs text-gray-500">{alert.symbol}</span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                <p className="text-sm mt-1">{alert.message}</p>
                
                {/* 价格信息 */}
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className="text-gray-600">
                    当前: <span className="font-semibold">${alert.current_price.toFixed(2)}</span>
                  </span>
                  {alert.critical_price && (
                    <span className="text-gray-600">
                      目标: <span className="font-semibold">${alert.critical_price.toFixed(2)}</span>
                    </span>
                  )}
                  {alert.distance_pct !== undefined && (
                    <span className={`font-semibold ${
                      Math.abs(alert.distance_pct) <= 1 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      距离: {alert.distance_pct > 0 ? '+' : ''}{alert.distance_pct.toFixed(2)}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {hasMore && (
          <div className="text-center text-sm text-gray-400 py-2">
            还有 {alerts.length - maxAlerts} 条预警...
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertPanel;
