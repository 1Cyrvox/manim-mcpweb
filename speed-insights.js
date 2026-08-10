// Import and inject Vercel Speed Insights
import { injectSpeedInsights } from '/assets/js/speed-insights.mjs';

// Initialize Speed Insights
// Note: Tracking only works in production (deployed on Vercel)
// In development mode, the package does not track data
injectSpeedInsights({
  // Enable debug mode in development
  debug: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
});
