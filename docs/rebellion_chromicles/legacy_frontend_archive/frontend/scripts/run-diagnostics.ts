// scripts/run-diagnostics.ts
import { runDiagnostics } from '../src/utils/diagnostics';

// Run the diagnostics
console.log('🚀 Starting System Diagnostics...');

runDiagnostics()
  .then(() => {
    console.log('✅ Diagnostics completed successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('❌ Diagnostics failed:', error);
    process.exit(1);
  });
