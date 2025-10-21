// services/circuitBreaker.ts
export type CircuitState = "CLOSED" | "OPEN" | "HALF_OPEN";
  
  interface CircuitBreakerOptions {
    name: string;
    maxFailures: number;
    resetTimeout: number;
    halfOpenMaxTrials: number;
    exponentialBackoffFactor: number;
  }
  
  export class CircuitBreaker {
    getDetailedState(): { state: string; failures: number; waitTime: number; } {
      return {
        state: this.state,
        failures: this.failures,
        waitTime: this.getWaitTime()
      };
    }

    getState(): CircuitState {
      return this.state;
    }

    private state: CircuitState = "CLOSED";
    private failures: number = 0;
    private maxFailures: number;
    private resetTimeout: number;
    private halfOpenMaxTrials: number;
    private halfOpenTrials: number = 0;
    private lastFailureTime: number | null = null;
    private exponentialBackoffFactor: number;
    private currentBackoff: number = 1;
    private name: string;
    
    canAttemptConnection(): boolean {
      // CLOSED state - everything is fine, allow connections
      if (this.state === "CLOSED") {
        return true;
      }
      
      // OPEN state - check if we should transition to HALF_OPEN
      if (this.state === "OPEN") {
        if (this.lastFailureTime && Date.now() - this.lastFailureTime >= this.resetTimeout) {
          // Enough time has passed, try half-open
          this.state = "HALF_OPEN";
          console.log('⚡ Circuit breaker transitioning to HALF_OPEN');
          return true;
        }
        // Still in timeout period
        return false;
      }
      
      // HALF_OPEN state - allow limited attempts
      if (this.state === "HALF_OPEN") {
        // You might want to track attempt count here
        return true;
      }
      
      return false; // Default deny
    }
 
  
    constructor(options: CircuitBreakerOptions) {
      this.name = options.name;
      this.maxFailures = options.maxFailures;
      this.resetTimeout = options.resetTimeout;
      this.halfOpenMaxTrials = options.halfOpenMaxTrials;
      this.exponentialBackoffFactor = options.exponentialBackoffFactor;
      
      console.log(`Circuit Breaker '${this.name}' initialized`);
    }
  
    private calculateBackoff(): number {
      const backoff = Math.min(
        this.resetTimeout,
        this.currentBackoff * Math.pow(this.exponentialBackoffFactor, Math.min(this.failures, 8))
      );
      return backoff;
    }
  
    getWaitTime(): number {
      if (this.state === "OPEN" && this.lastFailureTime) {
        const backoff = this.calculateBackoff();
        const timeSinceFailure = (Date.now() - this.lastFailureTime) / 1000;
        return Math.max(0, backoff - timeSinceFailure);
      }
      return 0;
    }
  
    recordSuccess(): void {
      const prevState = this.state;
      
      if (this.state === "HALF_OPEN") {
        this.halfOpenTrials++;
        
        if (this.halfOpenTrials >= this.halfOpenMaxTrials) {
          this.reset();
          console.log(`Circuit Breaker '${this.name}': ${prevState} → ${this.state}`);
        }
      }
      
      if (this.state === "CLOSED") {
        this.failures = 0;
        this.currentBackoff = 1;
      }
    }
    reset() {
      this.state = "CLOSED";
      this.failures = 0;
      this.lastFailureTime = null;
      this.currentBackoff = 1;
    }
  
    recordFailure(): void {
      this.failures++;
      this.lastFailureTime = Date.now();
      if (this.failures >= this.maxFailures) {
        this.state = "OPEN";
        console.log(`Circuit breaker opened after ${this.failures} failures`);
      }
      const prevState = this.state;
      
      if (this.state === "HALF_OPEN") {
        this.state = "OPEN";
        console.log(`Circuit breaker state transition: ${prevState} → ${this.state}`);
      }
    }
}
