// Radio Button Component with Yes/No styling
interface RadioOptionProps {
  label: string;
  value: 'yes' | 'no' | 'pass' | 'fail' | 'valid' | 'invalid' | 'compliant' | 'violation' | 'none';
  selected: boolean;
  onChange: () => void;
  disabled?: boolean;
}

export function RadioOption({ label, value, selected, onChange, disabled }: RadioOptionProps) {
  const isPositive = value === 'yes' || value === 'pass' || value === 'valid' || value === 'compliant';
  const isNegative = value === 'no' || value === 'fail' || value === 'invalid' || value === 'violation';

  const getColor = () => {
    if (!selected) return '#e0e0e0';
    if (isPositive) return '#4CAF50';
    if (isNegative) return '#f44336';
    return '#2196F3';
  };

  return (
    <label
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '10px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        padding: '10px 15px',
        borderRadius: '8px',
        border: `2px solid ${selected ? getColor() : '#e0e0e0'}`,
        backgroundColor: selected ? `${getColor()}15` : 'transparent',
        transition: 'all 0.2s ease',
        opacity: disabled ? 0.5 : 1,
      }}
    >
      <input
        type="radio"
        checked={selected}
        onChange={onChange}
        disabled={disabled}
        style={{ display: 'none' }}
      />
      <div
        style={{
          width: '24px',
          height: '24px',
          borderRadius: '50%',
          border: `3px solid ${getColor()}`,
          backgroundColor: selected ? getColor() : 'transparent',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.2s ease',
        }}
      >
        {selected && (
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: 'white',
            }}
          />
        )}
      </div>
      <span style={{ color: '#000', fontWeight: '500' }}>{label}</span>
    </label>
  );
}

// Check Item Component for Pass/Fail questions
interface CheckItemProps {
  label: string;
  status: 'pass' | 'fail' | null;
  remarks: string;
  onStatusChange: (status: 'pass' | 'fail') => void;
  onRemarksChange: (remarks: string) => void;
  required?: boolean;
}

export function CheckItem({ 
  label, 
  status, 
  remarks, 
  onStatusChange, 
  onRemarksChange,
  required = true 
}: CheckItemProps) {
  return (
    <div
      style={{
        padding: '20px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        marginBottom: '15px',
        border: '1px solid #e0e0e0',
      }}
    >
      <div style={{ marginBottom: '15px' }}>
        <label style={{ 
          display: 'block', 
          fontWeight: '600', 
          color: '#000', 
          marginBottom: '10px',
          fontSize: '16px'
        }}>
          {label}
          {required && <span style={{ color: '#f44336', marginLeft: '4px' }}>*</span>}
        </label>
        
        <div style={{ display: 'flex', gap: '15px' }}>
          <RadioOption
            label="Pass"
            value="pass"
            selected={status === 'pass'}
            onChange={() => onStatusChange('pass')}
          />
          <RadioOption
            label="Fail"
            value="fail"
            selected={status === 'fail'}
            onChange={() => onStatusChange('fail')}
          />
        </div>
      </div>

      <div>
        <label style={{ 
          display: 'block', 
          fontWeight: '500', 
          color: '#666', 
          marginBottom: '8px',
          fontSize: '14px'
        }}>
          Remarks {status === 'fail' && <span style={{ color: '#f44336' }}>(Required when failed)</span>}
        </label>
        <textarea
          value={remarks}
          onChange={(e) => onRemarksChange(e.target.value)}
          className="input"
          rows={3}
          placeholder="Enter any observations or notes..."
          style={{ width: '100%', resize: 'vertical' }}
        />
      </div>
    </div>
  );
}
