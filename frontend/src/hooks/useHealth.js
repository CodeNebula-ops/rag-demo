import { useState, useEffect, useCallback } from 'react';
import { healthApi } from '../services/api';

export function useHealth() {
  const [health, setHealth] = useState({
    status: 'checking',
    postgres: 'checking',
    qdrant: 'checking',
    llm: 'checking',
  });

  const checkHealth = useCallback(async () => {
    try {
      const { data } = await healthApi.check();
      setHealth(data);
    } catch {
      setHealth({
        status: 'error',
        postgres: 'error',
        qdrant: 'error',
        llm: 'error',
      });
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return health;
}
