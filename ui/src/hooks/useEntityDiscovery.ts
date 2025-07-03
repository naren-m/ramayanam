import { useState, useEffect, useCallback } from 'react';

interface DiscoverySettings {
  processAllKandas: boolean;
  confidence_threshold: number;
  max_entities_per_sloka: number;
  entity_types?: string[];
  parallel_processing?: boolean;
}

interface DiscoveredEntity {
  id: string;
  text: string;
  normalizedForm: string;
  type: 'Person' | 'Place' | 'Event' | 'Object' | 'Concept';
  confidence: number;
  sourceReferences: Array<{
    sloka_id: string;
    kanda: string;
    sarga: string;
    position: { start: number; end: number };
    context: string;
  }>;
  extractionMethod: 'nlp' | 'llm' | 'hybrid';
  validationStatus: 'pending' | 'validated' | 'rejected';
  epithets?: string[];
  alternativeNames?: string[];
}

interface EntityConflict {
  id: string;
  type: 'duplicate' | 'ambiguous' | 'classification';
  entities: DiscoveredEntity[];
  description: string;
  suggestedResolution: string;
}

interface DiscoveryProgress {
  percentage: number;
  currentKanda?: string;
  currentSarga?: string;
  processedSlokas: number;
  totalSlokas: number;
  entitiesFound: number;
  processingRate: number;
  estimatedTimeRemaining: number;
  status: 'running' | 'paused' | 'completed' | 'error';
}

interface Statistics {
  entityTypeCounts: Record<string, number>;
  confidenceDistribution: Record<string, number>;
  processingStats: {
    totalProcessingTime: number;
    averageConfidence: number;
    patternsMatched: number;
    uniqueEntitiesFound: number;
  };
  recentActivity?: Array<{
    type: 'discovery' | 'validation' | 'conflict';
    message: string;
    timestamp: string;
  }>;
}

export const useEntityDiscovery = () => {
  const [discoveryProgress, setDiscoveryProgress] = useState<DiscoveryProgress | null>(null);
  const [pendingEntities, setPendingEntities] = useState<DiscoveredEntity[]>([]);
  const [validatedEntities, setValidatedEntities] = useState<DiscoveredEntity[]>([]);
  const [conflictingEntities, setConflictingEntities] = useState<EntityConflict[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load existing entities and statistics
      const [entitiesResponse, statsResponse] = await Promise.all([
        fetch('/api/entity-discovery/pending?limit=100'),
        fetch('/api/entity-discovery/metrics')
      ]);

      if (entitiesResponse.ok) {
        const entitiesData = await entitiesResponse.json();
        // The /pending endpoint returns entities that are pending validation
        const entities = entitiesData.entities || [];
        setPendingEntities(entities);
        // For now, set validated entities to empty since we're only getting pending
        setValidatedEntities([]);
      }

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics(statsData.metrics);
      }

      // Check if discovery is currently running
      await checkDiscoveryStatus();
      
    } catch (error) {
      console.error('Failed to load initial data:', error);
      setError('Failed to load initial data');
    } finally {
      setLoading(false);
    }
  };

  const checkDiscoveryStatus = async () => {
    try {
      const response = await fetch('/api/entity-discovery/status');
      if (response.ok) {
        const statusData = await response.json();
        setIsRunning(statusData.status.is_running);
      } else {
        setIsRunning(false);
      }
    } catch (error) {
      console.error('Failed to check discovery status:', error);
      setIsRunning(false);
    }
  };

  const startDiscovery = useCallback(async (settings: DiscoverySettings) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/entity-discovery/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });

      if (!response.ok) {
        throw new Error('Failed to start entity discovery');
      }

      const result = await response.json();
      
      setIsRunning(true);
      setDiscoveryProgress({
        percentage: 0,
        processedSlokas: 0,
        totalSlokas: result.totalSlokas || 24000, // Approximate total
        entitiesFound: 0,
        processingRate: 0,
        estimatedTimeRemaining: 0,
        status: 'running'
      });

      // Start polling for progress updates
      startProgressPolling();

    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to start discovery');
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const stopDiscovery = useCallback(async () => {
    try {
      // This would send a stop signal to the backend
      setIsRunning(false);
      stopProgressPolling();
      
      if (discoveryProgress) {
        setDiscoveryProgress({
          ...discoveryProgress,
          status: 'paused'
        });
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to stop discovery');
    }
  }, [discoveryProgress]);

  const resetDiscovery = useCallback(async () => {
    try {
      setIsRunning(false);
      setDiscoveryProgress(null);
      setError(null);
      stopProgressPolling();
      
      // Reload initial data
      await loadInitialData();
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to reset discovery');
    }
  }, []);

  const startProgressPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval);
    }

    const interval = setInterval(async () => {
      try {
        // This would poll for real progress from the backend
        // For now, we'll simulate progress
        setDiscoveryProgress(prev => {
          if (!prev || prev.status !== 'running') return prev;
          
          const newPercentage = Math.min(prev.percentage + Math.random() * 2, 100);
          const newProcessedSlokas = Math.floor((newPercentage / 100) * prev.totalSlokas);
          const newEntitiesFound = Math.floor(newProcessedSlokas * 0.15); // Estimate 15% entity rate
          
          if (newPercentage >= 100) {
            setIsRunning(false);
            stopProgressPolling();
            return {
              ...prev,
              percentage: 100,
              processedSlokas: prev.totalSlokas,
              entitiesFound: newEntitiesFound,
              status: 'completed' as const
            };
          }
          
          return {
            ...prev,
            percentage: newPercentage,
            processedSlokas: newProcessedSlokas,
            entitiesFound: newEntitiesFound,
            processingRate: Math.random() * 50 + 20, // 20-70 slokas/min
            estimatedTimeRemaining: ((100 - newPercentage) / 100) * 30 // Estimate 30 minutes total
          };
        });

        // Refresh entity lists periodically
        if (Math.random() < 0.3) { // 30% chance each poll
          await loadInitialData();
        }

      } catch (error) {
        console.error('Error polling progress:', error);
      }
    }, 2000); // Poll every 2 seconds

    setPollInterval(interval);
  };

  const stopProgressPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval);
      setPollInterval(null);
    }
  };

  const validateEntity = useCallback(async (entityId: string, validation: {
    status: 'validated' | 'rejected';
    correctedType?: string;
    correctedName?: string;
    notes?: string;
  }) => {
    try {
      setLoading(true);
      setError(null);

      // Send validation to the backend
      const action = validation.status === 'validated' ? 'approve' : 'reject';
      const requestBody: any = {
        entity_ids: [entityId],
        action: action
      };

      // Add correction fields if provided
      if (validation.correctedName || validation.correctedType || validation.notes) {
        requestBody.corrections = {
          correctedName: validation.correctedName,
          correctedType: validation.correctedType,
          notes: validation.notes
        };
      }

      const response = await fetch('/api/entity-discovery/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error('Failed to validate entity');
      }

      const result = await response.json();
      console.log('Validation result:', result);
      
      // Update local state
      setPendingEntities(prev => prev.filter(e => e.id !== entityId));
      
      if (validation.status === 'validated') {
        const entity = pendingEntities.find(e => e.id === entityId);
        if (entity) {
          setValidatedEntities(prev => [...prev, { ...entity, validationStatus: 'validated' }]);
        }
      }
      
    } catch (error) {
      console.error('Validation error:', error);
      setError(error instanceof Error ? error.message : 'Failed to validate entity');
    } finally {
      setLoading(false);
    }
  }, [pendingEntities]);

  const resolveConflict = useCallback(async (conflictId: string, resolution: {
    action: 'merge' | 'separate' | 'reclassify';
    primaryEntityId?: string;
    newClassification?: string;
    notes?: string;
  }) => {
    try {
      // This would send conflict resolution to the backend
      console.log('Resolving conflict:', conflictId, resolution);
      
      // Update local state
      setConflictingEntities(prev => prev.filter(c => c.id !== conflictId));
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to resolve conflict');
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopProgressPolling();
    };
  }, []);

  return {
    discoveryProgress,
    pendingEntities,
    validatedEntities,
    conflictingEntities,
    statistics,
    isRunning,
    error,
    loading,
    startDiscovery,
    stopDiscovery,
    resetDiscovery,
    validateEntity,
    resolveConflict
  };
};