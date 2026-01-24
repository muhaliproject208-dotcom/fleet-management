// Progress Tracker Component for Multi-Step Form
interface ProgressTrackerProps {
  currentStep: number;
  totalSteps: number;
}

export default function ProgressTracker({ currentStep, totalSteps }: ProgressTrackerProps) {
  const percentage = Math.round((currentStep / totalSteps) * 100);

  return (
    <div style={{ marginBottom: '30px' }}>
      {/* Progress Bar */}
      <div style={{ 
        backgroundColor: '#e0e0e0', 
        borderRadius: '10px', 
        height: '8px',
        overflow: 'hidden',
        marginBottom: '15px'
      }}>
        <div 
          style={{ 
            backgroundColor: '#4CAF50', 
            height: '100%', 
            width: `${percentage}%`,
            transition: 'width 0.3s ease'
          }}
        />
      </div>

      {/* Step Counter */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        color: '#000'
      }}>
        <div style={{ fontSize: '14px', fontWeight: '500' }}>
          Step {currentStep} of {totalSteps}
        </div>
        <div style={{ fontSize: '14px', color: '#666' }}>
          {percentage}% Complete
        </div>
      </div>

      {/* Step Indicators */}
      <div style={{ 
        display: 'flex', 
        gap: '5px', 
        marginTop: '15px',
        flexWrap: 'wrap'
      }}>
        {Array.from({ length: totalSteps }, (_, i) => (
          <div
            key={i}
            style={{
              flex: '1 1 auto',
              minWidth: '30px',
              height: '6px',
              borderRadius: '3px',
              backgroundColor: 
                i < currentStep - 1 ? '#4CAF50' : // Completed
                i === currentStep - 1 ? '#2196F3' : // Current
                '#e0e0e0', // Not started
              transition: 'background-color 0.3s ease'
            }}
          />
        ))}
      </div>
    </div>
  );
}
