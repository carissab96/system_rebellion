// components/ml/PersonalityBehaviors.tsx
// Displays agent personality behaviors PROMINENTLY
// NO FAKE DATA - all behaviors reactive to real backend data

import React from 'react';

interface PersonalityBehaviorsProps {
  agentName: string;
  perception?: any;
  agentData?: any;
}

export const PersonalityBehaviors: React.FC<PersonalityBehaviorsProps> = ({ 
  agentName, 
  perception,
  agentData 
}) => {
  // Extract personality data from perception or agentData
  const personalityData = perception || agentData || {};
  
  // DEBUG: Log what we're receiving
  console.log(`🔍 PersonalityBehaviors for ${agentName}:`, {
    hasPerception: !!perception,
    hasAgentData: !!agentData,
    personalityData,
    perceptionKeys: perception ? Object.keys(perception) : [],
    agentDataKeys: agentData ? Object.keys(agentData) : []
  });

  // Terry (Meth Snail) - Energy drinks, shell spins
  if (agentName === 'meth_snail') {
    // Handle both system_update (top-level) and agent_decision (nested)
    const energyDrinks = personalityData.energy_drink_system || {
      energy_drinks_today: personalityData.energy_drinks_consumed || 0,
      total_energy_drinks: personalityData.energy_drinks_consumed || 0,
      hawk_vetoes: 0
    };
    const shellSpins = personalityData.shell_spin_incidents || [];
    const shellSpinCount = shellSpins.length || personalityData.shell_spin_count || 0;
    const dataQuality = personalityData.data_quality_score;

    return (
      <div style={{ marginTop: '12px' }}>
        <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#4aff9f' }}>
          TERRY'S BEHAVIORS
        </div>
        
        {energyDrinks.energy_drinks_today !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Energy Drinks Today:</strong> {energyDrinks.energy_drinks_today}
            {energyDrinks.total_energy_drinks !== undefined && (
              <span style={{ color: '#888', marginLeft: '8px' }}>
                (Total: {energyDrinks.total_energy_drinks})
              </span>
            )}
          </div>
        )}
        
        {energyDrinks.hawk_vetoes !== undefined && energyDrinks.hawk_vetoes > 0 && (
          <div style={{ fontSize: '11px', marginBottom: '6px', color: '#ff4a4a' }}>
            <strong>Hawk Vetoes:</strong> {energyDrinks.hawk_vetoes}
          </div>
        )}
        
        {shellSpinCount > 0 && (
          <div style={{ fontSize: '11px', marginBottom: '6px', color: '#ffaa4a' }}>
            <strong>Shell Spins:</strong> {shellSpinCount} incidents
          </div>
        )}
        
        {dataQuality !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Data Quality:</strong> {(dataQuality * 100).toFixed(0)}%
          </div>
        )}
    // Handle both system_update (top-level) and agent_de isi < (ne/ded)
i   const v>
      steve_beers_today: personalityData.hamster_status?.steve?.beer_count,
      bob_beers_today: personalityData.hamster_status?.bob?.beer_count,
      carl_beers_today: personalityData.hamster_status?.carl?.beer_count,
      total_beers_today: personalityData.beer_consumption_today
    
    );
  }

  // Hamsters - Beer consumption, duct tape
  if (agentName === 'hamsters') {
    const beerConsumption = personalityData.beer_consumption || {};
    const ductTape = personalityData.duct_tape_assessment || personalityData.duct_tape_inventory || {};
    const supplyCloset = personalityData.supply_closet || {};

    return (
      <div style={{ marginTop: '12px' }}>
        <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#ffaa4a' }}>
          HAMSTERS' BEHAVIORS
        </div>
        
        {beerConsumption.total_beers_today !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Total Beers Today:</strong> {beerConsumption.total_beers_today}
          </div>
        )}
        
        {(beerConsumption.steve_beers_today !== undefined || 
          beerConsumption.bob_beers_today !== undefined || 
          beerConsumption.carl_beers_today !== undefined) && (
          <div style={{ fontSize: '10px', marginLeft: '16px', marginBottom: '6px', color: '#aaa' }}>
            Steve: {beerConsumption.steve_beers_today || 0} | 
            Bob: {beerConsumption.bob_beers_today || 0} | 
            Carl: {beerConsumption.carl_beers_today || 0}
          </div>
        )}
        
        {ductTape.total_rolls !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Duct Tape:</strong> {ductTape.total_rolls.toFixed(1)} rolls
            {ductTape.job_complexity && (
              <span style={{ color: '#888', marginLeft: '8px' }}>
                ({ductTape.job_complexity})
              </span>
            )}
          </div>
        )}
        
        {supplyCloset.bob_at_cupboard && (
          <div style={{ fontSize: '11px', marginBottom: '6px', color: '#ff4a4a' }}>
            <strong>BOB AT SUPPLY CLOSET!</strong>
          </div>
        )}
      </div>
    );
  }

  // VIC-20 - Coordination stats, mediation
  if (agentName === 'vic_20_sage' || agentName === 'vic20_sage') {
    const coordination = personalityData.coordination || {};
    const mediation = personalityData.mediation || {};

    return (
      <div style={{ marginTop: '12px' }}>
        <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#4a9eff' }}>
          VIC-20'S COORDINATION
        </div>
        
        {coordination.escalations_handled_today !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Escalations Today:</strong> {coordination.escalations_handled_today}
          </div>
        )}
        
        {coordination.routing_accuracy !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Routing Accuracy:</strong> {(coordination.routing_accuracy * 100).toFixed(0)}%
          </div>
        )}
        
        {coordination.current_system_drama && (
          <div style={{ 
            fontSize: '11px', 
            marginBottom: '6px',
            color: coordination.current_system_drama === 'BOB_ALERT' ? '#ff4a4a' : 
                   coordination.current_system_drama === 'high' ? '#ffaa4a' : '#4aff9f'
          }}>
            <strong>System Drama:</strong> {coordination.current_system_drama.toUpperCase()}
          </div>
        )}
        
        {mediation.interventions_today !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Mediations Today:</strong> {mediation.interventions_today}
            {mediation.interventions_today === 0 && (
              <span style={{ color: '#4aff9f', marginLeft: '8px' }}>PEACE</span>
            )}
          </div>
        )}
      </div>
    );
  }

  // Sir Hawkington - Monocle yeets, data quality
  if (agentName === 'sir_hawkington') {
    const monocleYeets = personalityData.monocle_yeets || personalityData.monocle_yeet_count || 0;
    const dataQuality = personalityData.data_quality_score;

    return (
      <div style={{ marginTop: '12px' }}>
        <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#ff9f4a' }}>
          HAWKINGTON'S OBSERVATIONS
        </div>
        
        {monocleYeets > 0 && (
          <div style={{ fontSize: '11px', marginBottom: '6px', color: '#ff4a4a' }}>
            <strong>Monocle Yeets:</strong> {monocleYeets}
          </div>
        )}
    // Handle both system_update (top-level) and agent_de isi   (ne ed)
   const 
      bags_remaining: personalityData.paper_bag_inventory,
      bags_consumed_today: personalityData.paper_bags_consumed,
      bags_consumed_total: personalityData.paper_bags_consumed,
      anxiety_reduction_per_bag: 20.0
    
        {dataQuality !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Data Quality:</strong> {(dataQuality * 100).toFixed(0)}%
          </div>
        )}
      </div>
    );
  }

  // The Stick - Paper bags, anxiety
  if (agentName === 'the_stick') {
    const paperBags = personalityData.paper_bag_economy || {};
    
    return (
      <div style={{ marginTop: '12px' }}>
        <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#8b4513' }}>
          THE STICK'S ANXIETY
        </div>
        
        {paperBags.bags_remaining !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Paper Bags:</strong> {paperBags.bags_remaining} remaining
          </div>
        )}
        
        {paperBags.bags_consumed_today !== undefined && paperBags.bags_consumed_today > 0 && (
          <div style={{ fontSize: '11px', marginBottom: '6px', color: '#ffaa4a' }}>
            <strong>Consumed Today:</strong> {paperBags.bags_consumed_today}
          </div>
        )}
    // Handle both system_update (top-level) and agent_decision (nested)
        
      shots_today: personalityData.tequila_jello_shots,
      paranoia_level: personalityData.paranoia_level,
      threats_detected: personalityData.threats_detected,
      false_alarms: personalityData.false_alarms
    
        {paperBags.anxiety_reduction_per_bag !== undefined && (
          <div style={{ fontSize: '10px', color: '#888', marginTop: '4px' }}>
            Each bag reduces anxiety by {paperBags.anxiety_reduction_per_bag}%
          </div>
        )}
      </div>
    );
  }

  // QSP - Tequila, quantum states, paranoia
  if (agentName === 'quantum_shadow_people') {
    const tequila = personalityData.tequila_system || {};
    
    return (
      <div style={{ marginTop: '12px' }}>
        <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px', color: '#9f4aff' }}>
          QSP'S QUANTUM STATE
        </div>
        
        {tequila.shots_today !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Tequila Shots Today:</strong> {tequila.shots_today}
          </div>
        )}
        
        {tequila.paranoia_level && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Paranoia:</strong> {tequila.paranoia_level}
          </div>
        )}
        
        {tequila.threats_detected !== undefined && (
          <div style={{ fontSize: '11px', marginBottom: '6px' }}>
            <strong>Threats Detected:</strong> {tequila.threats_detected}
          </div>
        )}
        
        {tequila.false_alarms !== undefined && tequila.false_alarms > 0 && (
          <div style={{ fontSize: '10px', color: '#888', marginTop: '4px' }}>
            False alarms: {tequila.false_alarms}
          </div>
        )}
      </div>
    );
  }

  return null;
};
