import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os

class MarketPipelineError(Exception):
    """Base exception for ML pipeline errors, enforcing loud failures."""
    pass

class DataColdStartError(MarketPipelineError):
    """Raised when insufficient historical data exists to run the pipeline."""
    pass

def generate_perception_data(num_samples: int = 1000) -> pd.DataFrame:
    """
    Perception Layer: Generates simulated market metrics.
    No silent fallbacks. If parameters are invalid, we fail loud.
    """
    if num_samples <= 0:
        raise ValueError(f"num_samples must be strictly positive. Received: {num_samples}")
        
    np.random.seed(42)  # Single source of truth for reproducibility here
    dates = pd.date_range(start='2020-01-01', periods=num_samples, freq='D')
    
    volume = np.random.normal(loc=10000, scale=2000, size=num_samples)
    volatility = np.random.uniform(low=0.01, high=0.05, size=num_samples)
    sentiment_score = np.random.uniform(low=-1, high=1, size=num_samples)
    
    base_price = 100
    price_changes = (sentiment_score * 5) + (volume / 5000) - (volatility * 100) + np.random.normal(0, 1, num_samples)
    prices = base_price + np.cumsum(price_changes)
    
    df = pd.DataFrame({
        'date': dates,
        'volume': volume,
        'volatility': volatility,
        'sentiment_score': sentiment_score,
        'price': prices
    })
    
    df['target_next_day_price'] = df['price'].shift(-1)
    df = df.dropna()
    
    # Cold-Start Handling: Explicit threshold for minimum viable data
    if df.empty or len(df) < 10:
        raise DataColdStartError("Cold start: Not enough historical data to generate reliable signals (minimum 10 rows required).")
        
    return df

def routing_and_reasoning_layer(df: pd.DataFrame) -> tuple:
    """
    Reasoning Component: Trains the model and generates predictions.
    """
    if df.empty:
        raise DataColdStartError("Cannot route empty dataframe to reasoning layer.")
        
    features = ['volume', 'volatility', 'sentiment_score', 'price']
    
    # Validation constraint check
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        raise MarketPipelineError(f"Missing required features: {missing_features}")
        
    X = df[features]
    y = df['target_next_day_price']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"Model Evaluation -> MAE: {mae:.2f}, RMSE: {rmse:.2f}")
    
    results_df = X_test.copy()
    results_df['date'] = df.loc[X_test.index, 'date']
    results_df['actual_price'] = y_test
    results_df['predicted_price'] = predictions
    
    return model, results_df

def execution_layer(results_df: pd.DataFrame, output_path: str) -> None:
    """
    Action/Execution Layer: Publishes the predictions. 
    """
    if results_df.empty:
        raise MarketPipelineError("Execution layer received empty results. Aborting write to prevent silent data loss.")
        
    try:
        # Reorder columns for readability
        cols = ['date', 'actual_price', 'predicted_price', 'volume', 'volatility', 'sentiment_score', 'price']
        results_df = results_df[cols]
        results_df.to_csv(output_path, index=False)
        print(f"Successfully saved predictions to {output_path}")
    except Exception as e:
        raise MarketPipelineError(f"Failed to execute action (save predictions): {str(e)}") from e

def main():
    output_file = "/home/carissa/system_rebellion/market_predictions.csv"
    print("Starting ML Pipeline Execution...")
    try:
        data = generate_perception_data(num_samples=500)
        model, predictions = routing_and_reasoning_layer(data)
        execution_layer(predictions, output_file)
    except Exception as e:
        print(f"PIPELINE HALTED FATALLY: {e}")
        raise

if __name__ == "__main__":
    main()
