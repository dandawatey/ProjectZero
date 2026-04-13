import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

export function useCxoPortfolio() {
  return useQuery({
    queryKey: ['cxo-portfolio'],
    queryFn: api.cxo.portfolio,
    staleTime: 5 * 60 * 1000, // 5 min
  });
}

export function useCxoProject(key: string) {
  return useQuery({
    queryKey: ['cxo-project', key],
    queryFn: () => api.cxo.project(key),
    enabled: !!key,
    staleTime: 5 * 60 * 1000,
  });
}

export function useRefreshCxoProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (key: string) => api.cxo.refresh(key),
    onSuccess: (_, key) => {
      qc.invalidateQueries({ queryKey: ['cxo-project', key] });
      qc.invalidateQueries({ queryKey: ['cxo-portfolio'] });
    },
  });
}
