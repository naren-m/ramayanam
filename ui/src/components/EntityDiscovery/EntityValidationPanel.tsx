import React, { useState } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Eye, 
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  Edit,
  Search,
  Filter,
  User,
  MapPin,
  Calendar,
  BookOpen,
  Target
} from 'lucide-react';

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
  suggestedMerges?: string[];
}

interface EntityConflict {
  id: string;
  type: 'duplicate' | 'ambiguous' | 'classification';
  entities: DiscoveredEntity[];
  description: string;
  suggestedResolution: string;
}

interface EntityValidationPanelProps {
  pendingEntities?: DiscoveredEntity[];
  conflictingEntities?: EntityConflict[];
  onValidateEntity: (entityId: string, validation: { 
    status: 'validated' | 'rejected';
    correctedType?: string;
    correctedName?: string;
    notes?: string;
  }) => void;
  onResolveConflict: (conflictId: string, resolution: {
    action: 'merge' | 'separate' | 'reclassify';
    primaryEntityId?: string;
    newClassification?: string;
    notes?: string;
  }) => void;
}

export const EntityValidationPanel: React.FC<EntityValidationPanelProps> = ({
  pendingEntities = [],
  conflictingEntities = [],
  onValidateEntity,
  onResolveConflict
}) => {
  const [activeSection, setActiveSection] = useState<'pending' | 'conflicts'>('pending');
  const [selectedEntity, setSelectedEntity] = useState<DiscoveredEntity | null>(null);
  const [selectedConflict, setSelectedConflict] = useState<EntityConflict | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingEntity, setEditingEntity] = useState<DiscoveredEntity | null>(null);
  const [editForm, setEditForm] = useState({
    normalizedForm: '',
    type: 'Person' as 'Person' | 'Place' | 'Event' | 'Object' | 'Concept',
    notes: ''
  });

  const entityTypeIcons = {
    Person: User,
    Place: MapPin,
    Event: Calendar,
    Object: Target,
    Concept: BookOpen
  };

  const getEntityTypeColor = (type: string) => {
    const colors = {
      Person: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30',
      Place: 'text-green-600 bg-green-100 dark:bg-green-900/30',
      Event: 'text-purple-600 bg-purple-100 dark:bg-purple-900/30',
      Object: 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30',
      Concept: 'text-indigo-600 bg-indigo-100 dark:bg-indigo-900/30'
    };
    return colors[type as keyof typeof colors] || 'text-gray-600 bg-gray-100 dark:bg-gray-700';
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100 dark:bg-green-900/30';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30';
    return 'text-red-600 bg-red-100 dark:bg-red-900/30';
  };

  const filteredPendingEntities = pendingEntities.filter(entity => {
    const matchesType = filterType === 'all' || entity.type === filterType;
    const matchesSearch = searchQuery === '' || 
      entity.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entity.normalizedForm.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const handleValidateEntity = (entityId: string, status: 'validated' | 'rejected') => {
    onValidateEntity(entityId, { status });
    setSelectedEntity(null);
  };

  const handleEditEntity = (entity: DiscoveredEntity) => {
    setEditingEntity(entity);
    setEditForm({
      normalizedForm: entity.normalizedForm,
      type: entity.type,
      notes: ''
    });
  };

  const handleSaveEdit = () => {
    if (editingEntity) {
      onValidateEntity(editingEntity.id, {
        status: 'validated',
        correctedName: editForm.normalizedForm,
        correctedType: editForm.type,
        notes: editForm.notes
      });
      setEditingEntity(null);
      setSelectedEntity(null);
    }
  };

  const handleCancelEdit = () => {
    setEditingEntity(null);
  };

  return (
    <div className="space-y-6" data-testid="entity-validation-panel">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
            Entity Validation
          </h3>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {pendingEntities.length} pending • {conflictingEntities.length} conflicts
          </div>
        </div>

        {/* Section Tabs */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg mb-4">
          <button
            onClick={() => setActiveSection('pending')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeSection === 'pending'
                ? 'bg-white dark:bg-gray-800 text-orange-600 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
            }`}
          >
            Pending Validation ({pendingEntities.length})
          </button>
          <button
            onClick={() => setActiveSection('conflicts')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeSection === 'conflicts'
                ? 'bg-white dark:bg-gray-800 text-orange-600 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
            }`}
          >
            Conflicts ({conflictingEntities.length})
          </button>
        </div>

        {/* Filters */}
        {activeSection === 'pending' && (
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search entities..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
            >
              <option value="all">All Types</option>
              <option value="Person">Person</option>
              <option value="Place">Place</option>
              <option value="Event">Event</option>
              <option value="Object">Object</option>
              <option value="Concept">Concept</option>
            </select>
          </div>
        )}
      </div>

      {/* Content */}
      {activeSection === 'pending' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Entity List */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-gray-200 dark:border-gray-600">
              <h4 className="font-medium text-gray-800 dark:text-gray-200">
                Entities Awaiting Validation
              </h4>
            </div>
            <div className="space-y-2 p-4">
              {filteredPendingEntities.map((entity) => {
                const IconComponent = entityTypeIcons[entity.type];
                return (
                  <div
                    key={entity.id}
                    onClick={() => setSelectedEntity(entity)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedEntity?.id === entity.id
                        ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/30'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className={`p-1 rounded ${getEntityTypeColor(entity.type)}`}>
                          <IconComponent className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h5 className="font-medium text-gray-800 dark:text-gray-200 truncate">
                            {entity.normalizedForm}
                          </h5>
                          <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                            {entity.text} • {entity.sourceReferences.length} mentions
                          </p>
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(entity.confidence)}`}>
                        {Math.round(entity.confidence * 100)}%
                      </div>
                    </div>
                  </div>
                );
              })}
              {filteredPendingEntities.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No entities awaiting validation</p>
                </div>
              )}
            </div>
          </div>

          {/* Entity Details */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600">
            {selectedEntity ? (
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      {selectedEntity.normalizedForm}
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Original: {selectedEntity.text}
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${getEntityTypeColor(selectedEntity.type)}`}>
                    {selectedEntity.type}
                  </div>
                </div>

                {/* Entity Information */}
                <div className="space-y-4 mb-6">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Confidence Score</label>
                    <div className="mt-1">
                      <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(selectedEntity.confidence)}`}>
                        {Math.round(selectedEntity.confidence * 100)}% confidence
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Extraction Method</label>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 capitalize">
                      {selectedEntity.extractionMethod}
                    </p>
                  </div>

                  {selectedEntity.epithets && selectedEntity.epithets.length > 0 && (
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Epithets</label>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {selectedEntity.epithets.map((epithet, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded-md text-gray-600 dark:text-gray-400"
                          >
                            {epithet}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Source References ({selectedEntity.sourceReferences.length})
                    </label>
                    <div className="mt-2 space-y-2 max-h-32 overflow-y-auto">
                      {selectedEntity.sourceReferences.slice(0, 3).map((ref, index) => (
                        <div
                          key={index}
                          className="p-2 bg-gray-50 dark:bg-gray-700 rounded text-xs"
                        >
                          <div className="font-medium text-gray-800 dark:text-gray-200">
                            {ref.kanda} {ref.sarga}.{ref.sloka_id}
                          </div>
                          <div className="text-gray-600 dark:text-gray-400 mt-1">
                            {ref.context}
                          </div>
                        </div>
                      ))}
                      {selectedEntity.sourceReferences.length > 3 && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                          +{selectedEntity.sourceReferences.length - 3} more references
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Validation Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={() => handleValidateEntity(selectedEntity.id, 'validated')}
                    className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                  >
                    <ThumbsUp className="w-4 h-4" />
                    Validate
                  </button>
                  <button
                    onClick={() => handleValidateEntity(selectedEntity.id, 'rejected')}
                    className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
                  >
                    <ThumbsDown className="w-4 h-4" />
                    Reject
                  </button>
                  <button 
                    onClick={() => handleEditEntity(selectedEntity)}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Select an entity to view details</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Conflicts Section */}
      {activeSection === 'conflicts' && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-600">
          <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-4">
            Entity Conflicts
          </h4>
          {conflictingEntities.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No conflicts detected</p>
            </div>
          ) : (
            <div className="space-y-4">
              {conflictingEntities.map((conflict) => (
                <div
                  key={conflict.id}
                  className="p-4 border border-orange-200 dark:border-orange-600 rounded-lg bg-orange-50 dark:bg-orange-900/30"
                >
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-orange-600 dark:text-orange-400 mt-0.5" />
                    <div className="flex-1">
                      <h5 className="font-medium text-gray-800 dark:text-gray-200">
                        {conflict.type} Conflict
                      </h5>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {conflict.description}
                      </p>
                      <div className="mt-3 flex gap-2">
                        {conflict.entities.map((entity, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded text-xs"
                          >
                            {entity.normalizedForm}
                          </span>
                        ))}
                      </div>
                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() => onResolveConflict(conflict.id, { action: 'merge' })}
                          className="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded transition-colors"
                        >
                          Merge
                        </button>
                        <button
                          onClick={() => onResolveConflict(conflict.id, { action: 'separate' })}
                          className="px-3 py-1 bg-gray-500 hover:bg-gray-600 text-white text-xs rounded transition-colors"
                        >
                          Keep Separate
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Edit Modal */}
      {editingEntity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Edit Entity: {editingEntity.text}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Normalized Form
                </label>
                <input
                  type="text"
                  value={editForm.normalizedForm}
                  onChange={(e) => setEditForm({ ...editForm, normalizedForm: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Entity Type
                </label>
                <select
                  value={editForm.type}
                  onChange={(e) => setEditForm({ ...editForm, type: e.target.value as typeof editForm.type })}
                  className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="Person">Person</option>
                  <option value="Place">Place</option>
                  <option value="Event">Event</option>
                  <option value="Object">Object</option>
                  <option value="Concept">Concept</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Notes (optional)
                </label>
                <textarea
                  value={editForm.notes}
                  onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500"
                  placeholder="Add any correction notes..."
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSaveEdit}
                className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
              >
                Save & Validate
              </button>
              <button
                onClick={handleCancelEdit}
                className="flex-1 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EntityValidationPanel;