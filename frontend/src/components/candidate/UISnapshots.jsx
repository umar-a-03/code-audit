import { useState } from 'react';

const UISnapshots = ({ screenshots, hostedUrl }) => {
  const [previewImage, setPreviewImage] = useState(null);

  // Check if there's a screenshot error (e.g., Playwright not installed)
  const hasError = screenshots?.error && typeof screenshots.error === 'string';

  // Filter out error keys and null values
  const validScreenshots = screenshots
    ? Object.entries(screenshots).filter(([key, value]) => value && key !== 'error')
    : [];

  // Check if project is hosted
  const isHosted = hostedUrl && !hasError && validScreenshots.length > 0;

  // Show error state if Playwright failed
  if (hasError && hostedUrl) {
    const isPlaywrightError = screenshots.error.includes('Playwright') || screenshots.error.includes('browser');
    return (
      <div className="glass-panel p-4 flex-1">
        <h3 className="text-xs font-bold text-neon-amber uppercase mb-4">[ UI_SNAPSHOTS ]</h3>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <span className="material-symbols-outlined text-4xl text-neon-amber mb-2">
            {isPlaywrightError ? 'browser_not_supported' : 'error'}
          </span>
          <p className="text-gray-400 font-mono text-xs">
            {isPlaywrightError ? 'SCREENSHOTS UNAVAILABLE' : 'CAPTURE FAILED'}
          </p>
          <p className="text-gray-600 font-mono text-[10px] mt-1">
            {isPlaywrightError
              ? 'Browser service not configured'
              : 'Could not capture screenshots'}
          </p>
        </div>
      </div>
    );
  }

  // Show not supported state - screenshots not available in current backend
  return (
    <div className="glass-panel p-4 flex-1">
      <h3 className="text-xs font-bold text-primary uppercase mb-4">[ UI_SNAPSHOTS ]</h3>
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <span className="material-symbols-outlined text-4xl text-gray-600 mb-2">cloud_off</span>
        <p className="text-gray-500 font-mono text-xs">NOT AVAILABLE</p>
        <p className="text-gray-600 font-mono text-[10px] mt-1">
          UI screenshots are not supported in the current version
        </p>
      </div>
    </div>
  );

  return (
    <div className="glass-panel p-4 flex-1">
      <h3 className="text-xs font-bold text-primary uppercase mb-4">[ UI_SNAPSHOTS ]</h3>
      <div className="grid grid-cols-2 gap-3 mb-4">
        {validScreenshots.slice(0, 4).map(([pageName, screenshotPath], index) => (
          <div
            key={index}
            className="border border-primary/40 p-1 relative group cursor-pointer hover:border-primary transition-colors"
            onClick={() => setPreviewImage({ name: pageName, path: screenshotPath })}
          >
            {/* Corner decorations */}
            <div className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-primary" />
            <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b border-r border-primary" />

            <div className="bg-black aspect-video overflow-hidden">
              <img
                className="w-full h-full object-cover opacity-70 group-hover:opacity-100 transition-opacity"
                src={`/api/submissions/screenshots/${screenshotPath.split('/').pop()}`}
                alt={pageName}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect fill="%23111" width="400" height="300"/><text fill="%23555" x="50%" y="50%" text-anchor="middle" dy=".3em" font-family="monospace" font-size="12">Preview unavailable</text></svg>';
                }}
              />
            </div>
            <div className="text-[9px] text-center mt-1 text-primary/70 uppercase">
              {pageName.replace(/_/g, ' ')}
            </div>
          </div>
        ))}
      </div>
      {validScreenshots.length === 0 && (
        <div className="text-center py-4">
          <p className="text-gray-500 font-mono text-xs">No screenshots available</p>
        </div>
      )}

      {/* Preview Modal */}
      {previewImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm"
          onClick={() => setPreviewImage(null)}
        >
          <div className="relative max-w-5xl max-h-[90vh] m-4" onClick={(e) => e.stopPropagation()}>
            {/* Close button */}
            <button
              className="absolute -top-10 right-0 text-white/70 hover:text-white transition-colors"
              onClick={() => setPreviewImage(null)}
            >
              <span className="material-symbols-outlined text-3xl">close</span>
            </button>

            {/* Image title */}
            <p className="text-center text-white font-mono text-sm mb-3 uppercase">
              {previewImage.name.replace(/_/g, ' ')}
            </p>

            {/* Image */}
            <img
              className="max-w-full max-h-[80vh] object-contain border border-white/20"
              src={`/api/submissions/screenshots/${previewImage.path.split('/').pop()}`}
              alt={previewImage.name}
            />

            {/* Hint */}
            <p className="text-center text-white/50 font-mono text-xs mt-3">
              Click outside to close
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UISnapshots;
