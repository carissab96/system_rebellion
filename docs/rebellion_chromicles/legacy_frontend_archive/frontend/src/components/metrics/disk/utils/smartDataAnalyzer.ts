import { SmartData } from '../tabs/types';

interface SmartAnalysisResult {
  issues: string[];
  criticalAttributes: {
    name: string;
    value: number;
    threshold: number;
    severity: 'warning' | 'critical';
  }[];
  healthScore: number; // 0-100 score
}

/**
 * Analyzes SMART data to identify potential disk issues
 */
export const analyzeSmartData = (smartData: SmartData): SmartAnalysisResult => {
  const issues: string[] = [];
  const criticalAttributes: SmartAnalysisResult['criticalAttributes'] = [];
  
  // Check overall SMART status
  if (smartData.status === 'failed') {
    issues.push('SMART overall status: FAILED. Disk replacement strongly recommended.');
  } else if (smartData.status === 'warning') {
    issues.push('SMART overall status: WARNING. Monitor disk closely for further degradation.');
  }
  
  // Check life remaining
  if (smartData.lifeRemaining < 10) {
    issues.push(`Disk has only ${smartData.lifeRemaining}% life remaining. Replacement recommended soon.`);
  } else if (smartData.lifeRemaining < 30) {
    issues.push(`Disk has ${smartData.lifeRemaining}% life remaining. Consider planning for replacement.`);
  }
  
  // Analyze specific SMART attributes
  smartData.attributes.forEach(attr => {
    if (attr.status === 'bad') {
      issues.push(`${attr.name} (${attr.id}) is critical: value ${attr.value} below threshold ${attr.threshold}.`);
      criticalAttributes.push({
        name: attr.name,
        value: attr.value,
        threshold: attr.threshold,
        severity: 'critical'
      });
    } else if (attr.status === 'warning') {
      issues.push(`${attr.name} (${attr.id}) is concerning: value ${attr.value} approaching threshold ${attr.threshold}.`);
      criticalAttributes.push({
        name: attr.name,
        value: attr.value,
        threshold: attr.threshold,
        severity: 'warning'
      });
    }
  });
  
  // Check specific critical attributes by ID
  const checkCriticalAttribute = (id: number, name: string) => {
    const attr = smartData.attributes.find(a => a.id === id);
    if (attr && attr.raw > 0) {
      issues.push(`${name} detected: ${attr.raw} events recorded. This can indicate imminent disk failure.`);
      criticalAttributes.push({
        name,
        value: attr.raw,
        threshold: 0,
        severity: 'critical'
      });
    }
  };
  
  // Check common critical attributes
  checkCriticalAttribute(5, 'Reallocated Sectors');
  checkCriticalAttribute(187, 'Reported Uncorrectable Errors');
  checkCriticalAttribute(197, 'Current Pending Sectors');
  checkCriticalAttribute(198, 'Offline Uncorrectable Sectors');
  
  // Calculate a health score (0-100)
  let healthScore = calculateHealthScore(smartData, criticalAttributes);
  
  return {
    issues,
    criticalAttributes,
    healthScore
  };
};

/**
 * Calculate a health score from SMART data
 */
const calculateHealthScore = (
  smartData: SmartData, 
  criticalAttributes: SmartAnalysisResult['criticalAttributes']
): number => {
  // Start with base score from life remaining
  let score = smartData.lifeRemaining;
  
  // Reduce score based on SMART status
  if (smartData.status === 'failed') {
    score = Math.min(score, 10); // Cap at 10 if failed
  } else if (smartData.status === 'warning') {
    score = Math.min(score, 50); // Cap at 50 if warning
  }
  
  // Reduce score based on critical attributes
  criticalAttributes.forEach(attr => {
    if (attr.severity === 'critical') {
      score -= 20; // Major reduction for critical attributes
    } else if (attr.severity === 'warning') {
      score -= 10; // Minor reduction for warning attributes
    }
  });
  
  // Ensure score stays in 0-100 range
  return Math.max(0, Math.min(100, score));
};

export default analyzeSmartData;
