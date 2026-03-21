/**
 * WebSocket Hook
 * 
 * 管理 WebSocket 连接和消息处理
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketMessage, PriceUpdate, AlertMessage, MatrixUpdate } from '../types';

type MessageHandler = (message: WebSocketMessage) => void;

interface UseWebSocketOptions {
  onPriceUpdate?: (data: PriceUpdate) => void;
  onAlert?: (data: AlertMessage) => void;
  onMatrixUpdate?: (data: MatrixUpdate) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<Event | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const subscribedSymbolsRef = useRef<string[]>([]);
  
  const {
    onPriceUpdate,
    onAlert,
    onMatrixUpdate,
    onError,
    onConnect,
    onDisconnect,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;
  
  // 连接 WebSocket
  const connect = useCallback(() => {
    // 关闭现有连接
    if (wsRef.current) {
      wsRef.current.close();
    }
    
    // 创建新连接
    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket 连接成功');
      setIsConnected(true);
      setError(null);
      reconnectAttemptsRef.current = 0;
      
      // 重新订阅之前订阅的股票
      if (subscribedSymbolsRef.current.length > 0) {
        subscribe(subscribedSymbolsRef.current);
      }
      
      onConnect?.();
    };
    
    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setLastMessage(message);
        
        // 根据消息类型调用对应回调
        switch (message.type) {
          case 'price_update':
            onPriceUpdate?.(message as PriceUpdate);
            break;
          case 'alert':
            onAlert?.(message as AlertMessage);
            break;
          case 'matrix_update':
            onMatrixUpdate?.(message as MatrixUpdate);
            break;
        }
      } catch (e) {
        console.error('解析 WebSocket 消息失败:', e);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket 连接关闭');
      setIsConnected(false);
      onDisconnect?.();
      
      // 尝试重连
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        reconnectAttemptsRef.current++;
        console.log(`尝试重连 (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
        
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, reconnectInterval);
      }
    };
    
    ws.onerror = (event) => {
      console.error('WebSocket 错误:', event);
      setError(event);
      onError?.(event);
    };
  }, [onPriceUpdate, onAlert, onMatrixUpdate, onError, onConnect, onDisconnect, reconnectInterval, maxReconnectAttempts]);
  
  // 断开连接
  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = maxReconnectAttempts; // 防止自动重连
  }, [maxReconnectAttempts]);
  
  // 订阅股票
  const subscribe = useCallback((symbols: string[]) => {
    subscribedSymbolsRef.current = symbols;
    
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        symbols: symbols,
      }));
    }
  }, []);
  
  // 发送消息
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, []);
  
  // 获取触发矩阵
  const getMatrix = useCallback((symbol: string) => {
    sendMessage({
      type: 'get_matrix',
      symbol: symbol,
    });
  }, [sendMessage]);
  
  // 执行压力测试
  const stressTest = useCallback((symbol: string, price: number) => {
    sendMessage({
      type: 'stress_test',
      symbol: symbol,
      price: price,
    });
  }, [sendMessage]);
  
  // 组件挂载时连接，卸载时断开
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  return {
    isConnected,
    lastMessage,
    error,
    connect,
    disconnect,
    subscribe,
    sendMessage,
    getMatrix,
    stressTest,
  };
};

export default useWebSocket;
