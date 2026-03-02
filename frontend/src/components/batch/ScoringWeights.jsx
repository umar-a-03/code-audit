import { useState } from 'react';

const ScoringWeights = ({ onWeightsChange }) => {
  const [weights, setWeights] = useState({
    codeQuality: 40,
    performance: 35,
    uiux: 25,
  });

  const handleWeightChange = (key, value) => {
    const newWeights = { ...weights, [key]: parseInt(value) || 0 };
    setWeights(newWeights);
    onWeightsChange?.(newWeights);
  };

  return (
    <div className="space-y-3">
      <label className="block text-xs text-primary/70 font-mono">SCORING_WEIGHTS</label>

      <div className="grid grid-cols-3 gap-3">
        {/* Code Quality */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Code Quality</label>
          <input
            type="number"
            min="0"
            max="100"
            value={weights.codeQuality}
            onChange={(e) => handleWeightChange('codeQuality', e.target.value)}
            className="w-full bg-black/50 border border-gray-700 text-white font-mono text-sm px-2 py-1.5 focus:border-primary focus:ring-0"
          />
        </div>

        {/* Performance */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">Performance</label>
          <input
            type="number"
            min="0"
            max="100"
            value={weights.performance}
            onChange={(e) => handleWeightChange('performance', e.target.value)}
            className="w-full bg-black/50 border border-gray-700 text-white font-mono text-sm px-2 py-1.5 focus:border-primary focus:ring-0"
          />
        </div>

        {/* UI/UX */}
        <div>
          <label className="block text-xs text-gray-400 mb-1">UI/UX</label>
          <input
            type="number"
            min="0"
            max="100"
            value={weights.uiux}
            onChange={(e) => handleWeightChange('uiux', e.target.value)}
            className="w-full bg-black/50 border border-gray-700 text-white font-mono text-sm px-2 py-1.5 focus:border-primary focus:ring-0"
          />
        </div>
      </div>

      {/* Total indicator */}
      <div className="flex justify-between text-xs">
        <span className="text-gray-500">Total:</span>
        <span className={`font-mono ${weights.codeQuality + weights.performance + weights.uiux === 100 ? 'text-green-400' : 'text-yellow-400'}`}>
          {weights.codeQuality + weights.performance + weights.uiux}%
        </span>
      </div>
    </div>
  );
};

export default ScoringWeights;
