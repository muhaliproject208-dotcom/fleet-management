// Progress Tracker Component for Multi-Step Form
interface ProgressTrackerProps {
  currentStep: number;
  totalSteps: number;
  completedSteps?: number[]; // Optional array of completed step numbers for visual indication
}

export default function ProgressTracker({ currentStep, totalSteps, completedSteps }: ProgressTrackerProps) {
  // Use completedSteps length if available, otherwise use currentStep
  const completedCount = completedSteps ? completedSteps.length : currentStep - 1;
  const percentage = Math.round((completedCount / totalSteps) * 100);

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
            backgroundColor: completedSteps ? '#4CAF50' : '#000', 
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
          {completedSteps && completedSteps.length > 0 && (
            <span style={{ color: '#4CAF50', marginLeft: '10px' }}>
              ({completedSteps.length} saved)
            </span>
          )}
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
        {Array.from({ length: totalSteps }, (_, i) => {
          const stepNumber = i + 1;
          // Determine if this step is completed based on completedSteps if available
          const isCompleted = completedSteps 
            ? completedSteps.includes(stepNumber)
            : i < currentStep - 1;
          const isCurrent = stepNumber === currentStep;
          
          return (
            <div
              key={i}
              style={{
                flex: '1 1 auto',
                minWidth: '30px',
                height: '6px',
                borderRadius: '3px',
                backgroundColor: 
                  isCompleted ? '#4CAF50' : // Completed (green)
                  isCurrent ? '#2196F3' : // Current (blue)
                  '#e0e0e0', // Not started
                transition: 'background-color 0.3s ease'
              }}
            />
          );
        })}
      </div>
    </div>
  );
}
