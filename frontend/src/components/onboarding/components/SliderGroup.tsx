// components/onboarding/components/SliderGroup.tsx
import React from 'react';

// The props interface, now with the optional 'description' property
interface SliderGroupProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  unit?: string;
  description?: string; // <-- THE FIX: Added the missing prop here
}

export const SliderGroup: React.FC<SliderGroupProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  unit = '',
  description, // <-- Receiving the prop
}) => {
  return (
    <div className="slider-group">
      <div className="slider-label-container">
        <label className="slider-label">{label}</label>
        {/* We now render the description if it exists */}
        {description && <p className="slider-description">{description}</p>}
      </div>
      <div className="slider-input-container">
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value, 10))}
          className="config-slider"
        />
        <span className="slider-value">
          {value}{unit}
        </span>
      </div>
    </div>
  );
};