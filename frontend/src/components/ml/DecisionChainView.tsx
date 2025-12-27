// components/ml/DecisionChainView.tsx
// Displays the full ML v2 decision chain: Perception → Reasoning → Action → Learning
// NO FAKE DATA - displays actual ML pipeline data from backend

import React from 'react';

interface DecisionChainViewProps {
  decision: {
    decision_id: string;
    timestamp: string;
    perception?: any;
    reasoning?: any;
    action_selection?: any;
    execution?: any;
    learning?: any;
  };
  agentName: string;
}

export const DecisionChainView: React.FC<DecisionChainViewProps> = ({ decision, agentName }) => {
  if (!decision.perception && !decision.reasoning && !decision.action_selection) {
    return null;
  }

  return (
    <div style={{
      border: '1px solid #333',
      borderRadius: '8px',
      padding: '16px',
      marginTop: '12px',
      backgroundColor: '#1a1a1a'
    }}>
      <div style={{
        fontSize: '14px',
        fontWeight: 'bold',
        marginBottom: '12px',
        color: '#fff'
      }}>
        ML Decision Chain
      </div>

      {/* STEP 1: PERCEPTION */}
      {decision.perception && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 'bold',
            color: '#4a9eff',
            marginBottom: '8px'
          }}>
            PERCEPTION
          </div>
          <div style={{
            fontSize: '11px',
            color: '#ccc',
            backgroundColor: '#0a0a0a',
            padding: '8px',
            borderRadius: '4px',
            fontFamily: 'monospace'
          }}>
            {JSON.stringify(decision.perception, null, 2)}
          </div>
        </div>
      )}

      {/* STEP 2: REASONING */}
      {decision.reasoning && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 'bold',
            color: '#ff9f4a',
            marginBottom: '8px'
          }}>
            REASONING
          </div>
          <div style={{ fontSize: '11px', color: '#ccc' }}>
            {decision.reasoning.root_cause && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Root Cause:</strong> {decision.reasoning.root_cause}
              </div>
            )}
            {decision.reasoning.confidence !== undefined && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Confidence:</strong> {(decision.reasoning.confidence * 100).toFixed(0)}%
              </div>
            )}
            {decision.reasoning.reasoning && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Analysis:</strong> {decision.reasoning.reasoning}
              </div>
            )}
            {decision.reasoning.primary_reason && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Primary Reason:</strong> {decision.reasoning.primary_reason}
              </div>
            )}
          </div>
        </div>
      )}

      {/* STEP 3: ACTION SELECTION */}
      {decision.action_selection && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 'bold',
            color: '#4aff9f',
            marginBottom: '8px'
          }}>
            ACTION SELECTION
          </div>
          <div style={{ fontSize: '11px', color: '#ccc' }}>
            {decision.action_selection.chosen_action && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Action:</strong> {decision.action_selection.chosen_action}
              </div>
            )}
            {decision.action_selection.action_type && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Type:</strong> {decision.action_selection.action_type}
              </div>
            )}
            {decision.action_selection.exploration !== undefined && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Exploration:</strong> {decision.action_selection.exploration ? 'Yes (exploring alternatives)' : 'No (exploiting best known)'}
              </div>
            )}
            {decision.action_selection.epsilon !== undefined && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Epsilon:</strong> {decision.action_selection.epsilon.toFixed(3)}
              </div>
            )}
            {decision.action_selection.alternatives_considered && decision.action_selection.alternatives_considered.length > 0 && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Alternatives:</strong> {decision.action_selection.alternatives_considered.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}

      {/* STEP 4: EXECUTION */}
      {decision.execution && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontSize: '12px',
            fontWeight: 'bold',
            color: '#ff4a9f',
            marginBottom: '8px'
          }}>
            EXECUTION
          </div>
          <div style={{ fontSize: '11px', color: '#ccc' }}>
            {decision.execution.success !== undefined && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Success:</strong> {decision.execution.success ? 'Yes' : 'No'}
              </div>
            )}
            {decision.execution.improvement_percentage !== undefined && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Improvement:</strong> {decision.execution.improvement_percentage.toFixed(1)}%
              </div>
            )}
            {decision.execution.metrics_before && decision.execution.metrics_after && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '8px',
                marginTop: '8px'
              }}>
                <div>
                  <strong>Before:</strong>
                  <div style={{ fontSize: '10px', marginTop: '4px' }}>
                    {Object.entries(decision.execution.metrics_before).map(([key, value]: [string, any]) => (
                      <div key={key}>{key}: {typeof value === 'number' ? value.toFixed(1) : value}</div>
                    ))}
                  </div>
                </div>
                <div>
                  <strong>After:</strong>
                  <div style={{ fontSize: '10px', marginTop: '4px' }}>
                    {Object.entries(decision.execution.metrics_after).map(([key, value]: [string, any]) => (
                      <div key={key}>{key}: {typeof value === 'number' ? value.toFixed(1) : value}</div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* STEP 5: LEARNING */}
      {decision.learning && (
        <div>
          <div style={{
            fontSize: '12px',
            fontWeight: 'bold',
            color: '#9f4aff',
            marginBottom: '8px'
          }}>
            LEARNING
          </div>
          <div style={{ fontSize: '11px', color: '#ccc' }}>
            {decision.learning.situation_fingerprint && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Fingerprint:</strong> {decision.learning.situation_fingerprint}
              </div>
            )}
            {decision.learning.stored !== undefined && (
              <div style={{ marginBottom: '4px' }}>
                <strong>Stored:</strong> {decision.learning.stored ? 'Yes' : 'No'}
              </div>
            )}
            {decision.learning.learning_record_id && (
              <div style={{ marginBottom: '4px', fontSize: '10px', color: '#888' }}>
                Record ID: {decision.learning.learning_record_id}
              </div>
            )}
          </div>
        </div>
      )}

      <div style={{
        fontSize: '10px',
        color: '#666',
        marginTop: '12px',
        paddingTop: '8px',
        borderTop: '1px solid #333'
      }}>
        Decision ID: {decision.decision_id} | {new Date(decision.timestamp).toLocaleString()}
      </div>
    </div>
  );
};
