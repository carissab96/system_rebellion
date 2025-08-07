 
// src/components/onboarding/SaveProgressModal.tsx


interface SaveProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveAndExit: () => void;
  onExitWithoutSaving: () => void;
  onSaveAndLogout: () => void; // New prop
}

export default function SaveProgressModal({ 
  isOpen, 
  onClose, 
  onSaveAndExit, 
  onExitWithoutSaving,
  onSaveAndLogout
}: SaveProgressModalProps) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onMouseDown={onClose}>
      <div className="modal-content" onMouseDown={e => e.stopPropagation()}>
        <header className="card-header text-center" style={{ position: 'relative' }}>
          <button 
            onClick={onClose}
            className="btn btn-ghost btn-sm"
            style={{ 
              position: 'absolute', 
              right: '1rem', 
              top: '1rem',
              padding: '0.25rem',
              minHeight: 'auto',
              fontSize: '1.2rem',
              lineHeight: '1'
            }}
            title="Close modal"
          >
            ×
          </button>
          <h2 className="card-title vic20-text">What would you like to do?</h2>
          <p className="card-subtitle mt-1">Choose how you'd like to proceed</p>
        </header>

        <div className="card-body d-flex flex-col gap-4">
          <p className="text-center">
            Your progress will be saved so you can pick up where you left off.
          </p>
          
          <div className="alert alert-info">
            <strong>What gets saved:</strong> Your preferences, agent selections, and current step
          </div>

          {/* Option Cards */}
          <div className="rebellion-grid rebellion-grid-cols-1 md:rebellion-grid-cols-2 gap-4">
            <div 
              className="btn btn-ghost"
              onClick={onSaveAndExit}
            >
              <h3 className="rebellion-text-primary">Save & Go to Dashboard</h3>
              <p className="text-sm text-base-content/70 mt-1">
                Stay logged in and explore the platform. Continue setup anytime from your dashboard.
              </p>
            </div>

            <div 
              className="btn btn-ghost"
              onClick={onSaveAndLogout}
            >
              <h3 className="rebellion-text-secondary">Save & Logout</h3>
              <p className="text-sm text-base-content/70 mt-1">
                Save your progress and log out. Resume setup when you return.
              </p>
            </div>

            <div 
              className="btn btn-ghost"
              onClick={onExitWithoutSaving}
            >
              <h3 className="rebellion-text-error">Start Over</h3>
              <p className="text-sm text-base-content/70 mt-1">
                Clear all progress and start fresh (cannot be undone).
              </p>
            </div>
          </div>
        </div>

        <footer className="card-footer d-flex justify-between align-center">
          <button 
            type="button" 
            onClick={onClose}
            className="btn btn-ghost"
          >
            Continue Setup
          </button>
          
          <div className="text-sm text-base-content/50">
            Choose an option above or continue setup
          </div>
        </footer>
      </div>
    </div>
  );
}