// services/backpressure.ts
interface BackpressureStats {
    droppedMessages: number;
    bufferSize: number;
    maxBufferSize: number;
    pressure: number;
    incomingRate: number;
    processingRate: number;
  }
  
  export class BackpressureHandler<T> {
    private buffer: T[] = [];
    private maxBufferSize: number;
    private incomingCount: number = 0;
    private processedCount: number = 0;
    private droppedMessages: number = 0;
    private lastRateCalculation: number = Date.now();
    private incomingRate: number = 0;
    private processingRate: number = 0;
    
    // Throttle settings from env or defaults
    private throttleThreshold: number;
    private minSleepMs: number;
    private maxSleepMs: number;
  
    constructor(options: {
      maxBufferSize?: number;
      throttleThreshold?: number;
      minSleepMs?: number;
      maxSleepMs?: number;
    } = {}) {
      this.maxBufferSize = options.maxBufferSize || 1000;
      this.throttleThreshold = options.throttleThreshold || 0.75;
      this.minSleepMs = options.minSleepMs || 50;
      this.maxSleepMs = options.maxSleepMs || 1200;
    }
  
    addItem(item: T): boolean {
      this.updateRates();
      this.incomingCount++;
  // ... continuing backpressure.ts

  if (this.buffer.length < this.maxBufferSize) {
    this.buffer.push(item);
    return true;
  }

  // Buffer full - apply sampling
  if (this.shouldSample()) {
    // Replace oldest item (FIFO)
    this.buffer.shift();
    this.buffer.push(item);
    return true;
  }

  // Item dropped
  this.droppedMessages++;
  return false;
}

getItems(count: number): T[] {
  const items = this.buffer.splice(0, Math.min(count, this.buffer.length));
  this.processedCount += items.length;
  this.updateRates();
  return items;
}

private updateRates(): void {
  const now = Date.now();
  const timeDiff = (now - this.lastRateCalculation) / 1000;
  
  if (timeDiff >= 5) { // Update every 5 seconds
    this.incomingRate = this.incomingCount / timeDiff;
    this.processingRate = this.processedCount / timeDiff;
    
    this.incomingCount = 0;
    this.processedCount = 0;
    this.lastRateCalculation = now;
  }
}

private shouldSample(): boolean {
  const pressure = this.getOverallPressure();
  const threshold = 1.0 - pressure ** 2;
  return Math.random() < threshold;
}

getBufferPressure(): number {
  return this.buffer.length / this.maxBufferSize;
}

getRatePressure(): number {
  if (this.processingRate <= 0 && this.incomingRate <= 0) return 0.0;
  if (this.processingRate <= 0 && this.incomingRate > 0) return 1.0;
  if (this.incomingRate <= 0) return 0.0;
  
  const ratio = this.incomingRate / Math.max(this.processingRate, 0.000001);
  return Math.min(1.0, ratio);
}

getOverallPressure(): number {
  return 0.4 * this.getBufferPressure() + 0.6 * this.getRatePressure();
}

shouldThrottle(): boolean {
  return this.getOverallPressure() >= this.throttleThreshold;
}

getWaitTime(): number {
  const pressure = this.getOverallPressure();
  if (pressure < this.throttleThreshold) return 0;

  const span = Math.max(0.000001, 1.0 - this.throttleThreshold);
  const norm = (pressure - this.throttleThreshold) / span;
  
  // Quadratic curve for wait time
  const sleepMs = this.minSleepMs + (this.maxSleepMs - this.minSleepMs) * (norm ** 2);
  
  // Add jitter
  const jitteredMs = sleepMs * (0.9 + 0.2 * Math.random());
  return Math.max(0, jitteredMs / 1000);
}

getStats(): BackpressureStats {
  return {
    bufferSize: this.buffer.length,
    maxBufferSize: this.maxBufferSize,
    pressure: this.getOverallPressure(),
    droppedMessages: this.droppedMessages,
    incomingRate: this.incomingRate,
    processingRate: this.processingRate
  };
}
clear(): void {
  this.buffer = [];
  this.droppedMessages = 0;
  this.incomingCount = 0;
  this.processedCount = 0;
}
}