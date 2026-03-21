import React from 'react';
import { ResonanceZone as ResonanceZoneType } from '../types';

interface ResonanceZoneProps {
  zones: ResonanceZoneType[];
  currentPrice: number;
}

export const ResonanceZone: React.FC<ResonanceZoneProps> = ({
  zones,
  currentPrice,
}) => {
  if (zones.length === 0) {
    return (
      <div className="card">
        <div className="card-header">共振区间检测</div>
        <div className="text-center text-gray-500 py-8">
          暂无多指标共振区间
          <div className="text-sm mt-2 text-gray-400">
            当多个技术指标的临界价格重合时，将显示高胜率买入区间
          </div>
        </div>
      </div>
    );
  }
  
  // 获取置信度颜色
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return 'bg-green-500';
    if (confidence >= 0.5) return 'bg-yellow-500';
    return 'bg-blue-500';
  };
  
  return (
    <div className="card">
      <div className="card-header flex justify-between items-center">
        <span>共振区间检测</span>
        <span className="text-sm font-normal text-gray-500">
          发现 {zones.length} 个共振区间
        </span>
      </div>
      
      <div className="space-y-4">
        {zones.map((zone, index) => {
          const isInZone = currentPrice >= zone.price_min && currentPrice <= zone.price_max;
          const distanceToCenter = Math.abs(zone.price_center - currentPrice) / currentPrice * 100;
          
          return (
            <div
              key={index}
              className={`p-4 rounded-lg border-2 transition-all ${
                isInZone
                  ? 'border-green-500 bg-green-50 shadow-md'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              {/* 区间头部 */}
              <div className="flex justify-between items-start mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold">
                      ${zone.price_min.toFixed(2)} - ${zone.price_max.toFixed(2)}
                    </span>
                    {isInZone && (
                      <span className="px-2 py-1 bg-green-500 text-white text-xs rounded-full animate-pulse">
                        已进入区间
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500">
                    中心价格: ${zone.price_center.toFixed(2)}
                    {zone.distance_pct !== undefined && (
                      <span className={`ml-2 ${
                        Math.abs(zone.distance_pct) <= 1 ? 'text-red-600 font-semibold' : ''
                      }`}>
                        ({zone.distance_pct > 0 ? '+' : ''}{zone.distance_pct.toFixed(2)}%)
                      </span>
                    )}
                  </div>
                </div>
                
                {/* 置信度指示器 */}
                <div className="text-right">
                  <div className="text-xs text-gray-500 mb-1">置信度</div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${getConfidenceColor(zone.confidence)} transition-all`}
                        style={{ width: `${zone.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold">
                      {(zone.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
              
              {/* 涉及的指标 */}
              <div className="flex flex-wrap gap-2 mb-3">
                {zone.indicators.map((indicator, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md"
                  >
                    {indicator}
                  </span>
                ))}
              </div>
              
              {/* 距离当前价格的视觉指示 */}
              {!isInZone && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>${zone.price_min.toFixed(2)}</span>
                    <span className="font-semibold text-gray-700">
                      当前 ${currentPrice.toFixed(2)}
                    </span>
                    <span>${zone.price_max.toFixed(2)}</span>
                  </div>
                  <div className="relative h-2 bg-gray-200 rounded-full">
                    {/* 区间标记 */}
                    <div
                      className="absolute h-full bg-blue-300 rounded-full"
                      style={{
                        left: '0%',
                        right: '0%',
                      }}
                    ></div>
                    {/* 当前价格标记 */}
                    <div
                      className="absolute w-3 h-3 bg-red-500 rounded-full border-2 border-white shadow"
                      style={{
                        top: '-2px',
                        left: `${Math.max(0, Math.min(100, 
                          ((currentPrice - zone.price_min) / (zone.price_max - zone.price_min)) * 100
                        ))}%`,
                        transform: 'translateX(-50%)',
                      }}
                    ></div>
                  </div>
                </div>
              )}
              
              {/* 交易建议 */}
              <div className={`mt-3 text-sm ${
                isInZone
                  ? 'text-green-700 font-semibold'
                  : zone.distance_pct !== undefined && Math.abs(zone.distance_pct) <= 2
                  ? 'text-yellow-700'
                  : 'text-gray-500'
              }`}>
                {isInZone
                  ? '✓ 强烈关注：当前价格处于高胜率共振区间'
                  : zone.distance_pct !== undefined && Math.abs(zone.distance_pct) <= 2
                  ? '⚠ 接近共振区间，建议密切关注'
                  : '观察中：等待价格进入共振区间'}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ResonanceZone;
