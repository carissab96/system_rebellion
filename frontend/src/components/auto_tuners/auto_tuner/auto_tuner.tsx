import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import { fetchSystemMetrics } from "../../../store/slices/metricsSlice";

// Renamed to AutoTunerComponent to avoid naming conflict
export const AutoTunerComponent: React.FC = () => {
    const dispatch = useAppDispatch();
    // Access the current metrics from the state
    const metrics = useAppSelector((state: any) => state.metrics.current);
    
    useEffect(() => {
        // Fetch metrics when component mounts
        dispatch(fetchSystemMetrics());
    }, [dispatch]);
    
    return (
        <div className="auto-tuner-container">
            <h1>System Auto Tuner</h1>
            <p>Optimizing your system resources in real-time</p>
            {metrics && (
                <div className="metrics-display">
                    <h2>Current System Metrics</h2>
                    <pre>{JSON.stringify(metrics, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};