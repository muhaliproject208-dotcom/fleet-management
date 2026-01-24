// Reusable Status Badge Component for Inspections
import { InspectionStatus } from '@/lib/api/inspections/types';

interface InspectionStatusBadgeProps {
  status: InspectionStatus;
  size?: 'sm' | 'md' | 'lg';
}

export default function InspectionStatusBadge({ status, size = 'md' }: InspectionStatusBadgeProps) {
  const getStatusStyles = (): { bg: string; text: string; border: string } => {
    switch (status) {
      case InspectionStatus.DRAFT:
        return { bg: '#f5f5f5', text: '#666', border: '#ccc' };
      case InspectionStatus.SUBMITTED:
        return { bg: '#f5f5f5', text: '#333', border: '#999' };
      case InspectionStatus.APPROVED:
        return { bg: '#000', text: '#fff', border: '#000' };
      case InspectionStatus.REJECTED:
        return { bg: '#fff', text: '#000', border: '#000' };
      case InspectionStatus.POST_TRIP_IN_PROGRESS:
        return { bg: '#FF9800', text: '#fff', border: '#FF9800' };
      case InspectionStatus.POST_TRIP_COMPLETED:
        return { bg: '#4CAF50', text: '#fff', border: '#4CAF50' };
      default:
        return { bg: '#f5f5f5', text: '#666', border: '#ccc' };
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case InspectionStatus.DRAFT:
        return 'edit_note';
      case InspectionStatus.SUBMITTED:
        return 'schedule';
      case InspectionStatus.APPROVED:
        return 'check_circle';
      case InspectionStatus.REJECTED:
        return 'cancel';
      case InspectionStatus.POST_TRIP_IN_PROGRESS:
        return 'hourglass_empty';
      case InspectionStatus.POST_TRIP_COMPLETED:
        return 'verified';
      default:
        return 'circle';
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case InspectionStatus.DRAFT:
        return 'Draft';
      case InspectionStatus.SUBMITTED:
        return 'Submitted';
      case InspectionStatus.APPROVED:
        return 'Approved';
      case InspectionStatus.REJECTED:
        return 'Rejected';
      case InspectionStatus.POST_TRIP_IN_PROGRESS:
        return 'Post-Trip In Progress';
      case InspectionStatus.POST_TRIP_COMPLETED:
        return 'Completed';
      default:
        return status;
    }
  };

  const sizeStyles = {
    sm: { padding: '4px 8px', fontSize: '12px', iconSize: '14px' },
    md: { padding: '6px 12px', fontSize: '14px', iconSize: '16px' },
    lg: { padding: '8px 16px', fontSize: '16px', iconSize: '18px' },
  };

  const styles = getStatusStyles();
  const sizeStyle = sizeStyles[size];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        borderRadius: '20px',
        border: `1px solid ${styles.border}`,
        backgroundColor: styles.bg,
        color: styles.text,
        fontWeight: 500,
        padding: sizeStyle.padding,
        fontSize: sizeStyle.fontSize,
      }}
    >
      <span className="material-icons" style={{ fontSize: sizeStyle.iconSize }}>{getStatusIcon()}</span>
      <span>{getStatusLabel()}</span>
    </span>
  );
}
