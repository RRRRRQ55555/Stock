import React from 'react';
import { TriggerMatrixResponse } from '../types';

interface TriggerMatrixProps {
  matrix: TriggerMatrixResponse | null;
  isLoading: boolean;
}

interface TriggerCardProps {
  title: string;
  price?: number;
  distance?: number;
  currentPrice: number;
  type: 'golden' | 'death' | 'oversold' | 'overbought' | 'neutral';
  indicator: string;
}

const TriggerCard: React.FC<TriggerCardProps> = ({
  title,
  price,
  distance,
  currentPrice,
  type,
  indicator,
}) => {
  // 根据类型确定颜色
  const getColors = () => {
    switch (type) {
      case 'golden':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'death':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'oversold':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'overbought':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-600';
    }
  };
  
  // 计算距离显示
  const getDistanceColor = (dist: number) => {
    if (Math.abs(dist) <= 1) return 'text-red-600 font-bold';
    if (Math.abs(dist) <= 3) return 'text-yellow-600';
    return 'text-gray-500';
  };
  
  return (
    <div className={`p-4 rounded-lg border ${getColors()} transition-all hover:shadow-md`}>
      <div className="text-xs uppercase tracking-wide opacity-70 mb-1">{indicator}</div>
      <div className="font-semibold text-sm mb-2">{title}</div>
      
      {price ? (
        <>
          <div className="text-2xl font-bold">
            ${price.toFixed(2)}
          </div>
          {distance !== undefined && (
            <div className={`text-sm mt-1 ${getDistanceColor(distance)}`}>
              {distance > 0 ? '+' : ''}{distance.toFixed(2)}%
              <span className="text-xs ml-1 opacity-70">
                ({distance > 0 ? '需上涨' : '需下跌'})
              </span>
            </div>
          )}
        </>
      ) : (
        <div className="text-lg opacity-50">无触发价格</div>
      )}
    </div>
  );
};

export const TriggerMatrix: React.FC<TriggerMatrixProps> = ({
  matrix,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="card-header">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }
  
  if (!matrix) {
    return (
      <div className="card">
        <div className="card-header">临界价格触发矩阵</div>
        <div className="text-center text-gray-500 py-8">
          请选择股票以查看临界价格
        </div>
      </div>
    );
  }
  
  const currentPrice = matrix.current_price;
  
  return (
    <div className="card">
      <div className="card-header flex justify-between items-center">
        <span>临界价格触发矩阵</span>
        <span className="text-sm font-normal text-gray-500">
          计算时间: {new Date(matrix.timestamp).toLocaleString()}
        </span>
      </div>
      
      {/* MACD 区域 */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
          MACD (12, 26, 9)
          <span className="ml-2 text-xs font-normal text-gray-500">
            DIF: {matrix.macd.dif.toFixed(4)} | Signal: {matrix.macd.signal.toFixed(4)}
          </span>
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <TriggerCard
            indicator="MACD"
            title="金叉临界价格"
            price={matrix.macd.golden_cross_price}
            distance={matrix.macd.distance_to_golden}
            currentPrice={currentPrice}
            type="golden"
          />
          <TriggerCard
            indicator="MACD"
            title="死叉临界价格"
            price={matrix.macd.death_cross_price}
            distance={matrix.macd.distance_to_death}
            currentPrice={currentPrice}
            type="death"
          />
        </div>
      </div>
      
      {/* 均线区域 */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
          均线 ({matrix.ma.short_period}/{matrix.ma.long_period})
          <span className="ml-2 text-xs font-normal text-gray-500">
            MA{matrix.ma.short_period}: {matrix.ma.ma_short.toFixed(2)} | 
            MA{matrix.ma.long_period}: {matrix.ma.ma_long.toFixed(2)} |
            {matrix.ma.is_bullish ? ' 多头排列' : ' 空头排列'}
          </span>
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <TriggerCard
            indicator="MA"
            title="金叉临界价格"
            price={matrix.ma.golden_cross_price}
            distance={matrix.ma.distance_to_golden}
            currentPrice={currentPrice}
            type="golden"
          />
          <TriggerCard
            indicator="MA"
            title="死叉临界价格"
            price={matrix.ma.death_cross_price}
            distance={matrix.ma.distance_to_death}
            currentPrice={currentPrice}
            type="death"
          />
        </div>
      </div>
      
      {/* KDJ 区域 */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
          KDJ (9, 3, 3)
          <span className="ml-2 text-xs font-normal text-gray-500">
            K: {matrix.kdj.k.toFixed(2)} | D: {matrix.kdj.d.toFixed(2)} | J: {matrix.kdj.j.toFixed(2)} |
            {' '}{matrix.kdj.zone === 'oversold' ? '超卖区' : matrix.kdj.zone === 'overbought' ? '超买区' : '震荡区'}
          </span>
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <TriggerCard
            indicator="KDJ"
            title="超卖临界价格 (J≤0)"
            price={matrix.kdj.oversold_price}
            distance={matrix.kdj.distance_to_oversold}
            currentPrice={currentPrice}
            type="oversold"
          />
          <TriggerCard
            indicator="KDJ"
            title="超买临界价格 (J≥100)"
            price={matrix.kdj.overbought_price}
            distance={matrix.kdj.distance_to_overbought}
            currentPrice={currentPrice}
            type="overbought"
          />
        </div>
      </div>
    </div>
  );
};

export default TriggerMatrix;
