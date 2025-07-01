import { GraphData, GraphNode, GraphEdge, KGEntity, KGRelationship, GraphApiResponse } from './types';

// Mock data service for testing the graph visualization
// This will be replaced with actual API calls
export class GraphDataService {
  private static API_BASE = '';

  // Convert KG entities to graph nodes
  static convertEntitiesToNodes(entities: KGEntity[]): GraphNode[] {
    return entities.map(entity => ({
      id: entity.kg_id,
      name: entity.labels.en,
      type: entity.entity_type as any,
      mentions: entity.properties.occurrence_count || 1,
      relevance: entity.properties.confidence_score || 0.5,
      confidence: entity.properties.confidence_score,
      epithets: entity.properties.epithets,
      sanskritName: entity.labels.sa
    }));
  }

  // Convert KG relationships to graph edges
  static convertRelationshipsToEdges(relationships: KGRelationship[]): GraphEdge[] {
    return relationships.map(rel => ({
      source: rel.source_entity_id,
      target: rel.target_entity_id,
      relationship: rel.relationship_type,
      weight: rel.confidence || 0.5,
      verified: rel.confidence > 0.8,
      confidence: rel.confidence
    }));
  }

  // Fetch entities from the existing KG API
  static async fetchEntities(limit: number = 50, entityType?: string): Promise<KGEntity[]> {
    try {
      const url = `${this.API_BASE}/api/kg/entities?limit=${limit}${entityType ? `&type=${entityType}` : ''}`;
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        return data.entities;
      }
      throw new Error('Failed to fetch entities');
    } catch (error) {
      console.error('Error fetching entities:', error);
      
      // Return mock data for testing
      return this.getMockEntities();
    }
  }

  // Search entities using existing API
  static async searchEntities(query: string, entityType?: string): Promise<KGEntity[]> {
    try {
      const url = `${this.API_BASE}/api/kg/search?q=${encodeURIComponent(query)}${entityType ? `&type=${entityType}` : ''}`;
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        return data.entities;
      }
      throw new Error('Search failed');
    } catch (error) {
      console.error('Error searching entities:', error);
      
      // Return filtered mock data for testing
      return this.getMockEntities().filter(entity => 
        entity.labels.en.toLowerCase().includes(query.toLowerCase()) ||
        (entity.labels.sa && entity.labels.sa.toLowerCase().includes(query.toLowerCase()))
      );
    }
  }

  // Create graph data for visualization
  static async createGraphData(
    centerEntity?: string, 
    maxNodes: number = 50,
    includeRelationships: boolean = true
  ): Promise<GraphData> {
    try {
      let entities: KGEntity[];
      
      if (centerEntity) {
        // If we have a center entity, search for it and related entities
        entities = await this.searchEntities(centerEntity);
        
        // Add some related entities (this would normally come from a relationship API)
        if (entities.length < maxNodes) {
          const additionalEntities = await this.fetchEntities(maxNodes - entities.length);
          entities = [...entities, ...additionalEntities];
        }
      } else {
        // Fetch general entities
        entities = await this.fetchEntities(maxNodes);
      }

      const nodes = this.convertEntitiesToNodes(entities.slice(0, maxNodes));
      
      let edges: GraphEdge[] = [];
      if (includeRelationships) {
        // For now, create mock relationships between entities
        // This would normally come from the relationships API
        edges = this.generateMockRelationships(nodes);
      }

      return {
        nodes,
        edges,
        metadata: {
          centerEntity,
          totalEntities: entities.length,
          maxDepth: includeRelationships ? 2 : 1
        }
      };
    } catch (error) {
      console.error('Error creating graph data:', error);
      
      // Return complete mock data
      return this.getMockGraphData();
    }
  }

  // Generate mock relationships for testing
  private static generateMockRelationships(nodes: GraphNode[]): GraphEdge[] {
    const edges: GraphEdge[] = [];
    const maxEdges = Math.min(nodes.length * 2, 100); // Limit edges to avoid clutter
    
    // Create some meaningful relationships
    const relationships = [
      'related_to',
      'father_of',
      'brother_of',
      'friend_of',
      'enemy_of',
      'located_in',
      'ruler_of',
      'born_in',
      'married_to',
      'teacher_of'
    ];

    for (let i = 0; i < maxEdges && i < nodes.length - 1; i++) {
      const source = nodes[i];
      const targetIndex = Math.floor(Math.random() * (nodes.length - i - 1)) + i + 1;
      const target = nodes[targetIndex];
      
      // Choose relationship based on entity types
      let relationship = 'related_to';
      if (source.type === 'Person' && target.type === 'Person') {
        const personRelations = ['father_of', 'brother_of', 'friend_of', 'enemy_of', 'married_to', 'teacher_of'];
        relationship = personRelations[Math.floor(Math.random() * personRelations.length)];
      } else if (source.type === 'Person' && target.type === 'Place') {
        const placeRelations = ['born_in', 'ruler_of', 'located_in'];
        relationship = placeRelations[Math.floor(Math.random() * placeRelations.length)];
      }
      
      edges.push({
        source: source.id,
        target: target.id,
        relationship,
        weight: Math.random() * 0.5 + 0.5, // 0.5 to 1.0
        verified: Math.random() > 0.3,
        confidence: Math.random() * 0.4 + 0.6 // 0.6 to 1.0
      });
    }
    
    return edges;
  }

  // Mock entities for testing when API is not available
  private static getMockEntities(): KGEntity[] {
    return [
      {
        kg_id: 'rama',
        entity_type: 'Person',
        labels: { en: 'Rama', sa: 'राम' },
        properties: {
          confidence_score: 0.95,
          occurrence_count: 1250,
          epithets: ['मर्यादापुरुषोत्तम', 'कोसलेन्द्र', 'रघुनन्दन']
        }
      },
      {
        kg_id: 'sita',
        entity_type: 'Person',
        labels: { en: 'Sita', sa: 'सीता' },
        properties: {
          confidence_score: 0.92,
          occurrence_count: 890,
          epithets: ['जानकी', 'वैदेही', 'मिथिलेशकुमारी']
        }
      },
      {
        kg_id: 'hanuman',
        entity_type: 'Person',
        labels: { en: 'Hanuman', sa: 'हनुमान्' },
        properties: {
          confidence_score: 0.94,
          occurrence_count: 680,
          epithets: ['मारुतिः', 'वायुपुत्र', 'अञ्जनेय']
        }
      },
      {
        kg_id: 'ravana',
        entity_type: 'Person',
        labels: { en: 'Ravana', sa: 'रावण' },
        properties: {
          confidence_score: 0.91,
          occurrence_count: 520,
          epithets: ['दशग्रीव', 'लङ्केश', 'राक्षसराज']
        }
      },
      {
        kg_id: 'ayodhya',
        entity_type: 'Place',
        labels: { en: 'Ayodhya', sa: 'अयोध्या' },
        properties: {
          confidence_score: 0.88,
          occurrence_count: 340,
          epithets: ['कोसलराजधानी']
        }
      },
      {
        kg_id: 'lanka',
        entity_type: 'Place',
        labels: { en: 'Lanka', sa: 'लङ्का' },
        properties: {
          confidence_score: 0.85,
          occurrence_count: 280,
          epithets: ['स्वर्णमयी', 'राक्षसपुरी']
        }
      },
      {
        kg_id: 'dharma',
        entity_type: 'Concept',
        labels: { en: 'Dharma', sa: 'धर्म' },
        properties: {
          confidence_score: 0.82,
          occurrence_count: 180,
          epithets: ['सनातन']
        }
      },
      {
        kg_id: 'exile',
        entity_type: 'Event',
        labels: { en: 'Exile', sa: 'वनवास' },
        properties: {
          confidence_score: 0.79,
          occurrence_count: 150,
          epithets: ['चतुर्दशवर्षीय']
        }
      }
    ];
  }

  // Complete mock graph data for testing
  private static getMockGraphData(): GraphData {
    const entities = this.getMockEntities();
    const nodes = this.convertEntitiesToNodes(entities);
    const edges = this.generateMockRelationships(nodes);
    
    return {
      nodes,
      edges,
      metadata: {
        totalEntities: entities.length,
        maxDepth: 2
      }
    };
  }

  // API endpoint for future backend support
  static async fetchGraphData(entityId: string): Promise<GraphApiResponse> {
    try {
      const response = await fetch(`${this.API_BASE}/api/kg/graph-data/${entityId}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching graph data:', error);
      
      // Return mock response
      const mockData = this.getMockGraphData();
      return {
        success: true,
        entities: this.getMockEntities(),
        relationships: [],
        center_entity: entityId,
        max_depth: 2
      };
    }
  }

  // Find path between two entities (for future implementation)
  static async findPath(sourceId: string, targetId: string): Promise<any> {
    // This would implement pathfinding algorithm
    // For now, return empty result
    return {
      path: [],
      distance: 0,
      relationships: []
    };
  }
}