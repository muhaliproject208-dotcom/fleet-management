// Reusable Status Badge Component for Inspections
import { InspectionStatus } from '@/lib/api/inspections/types';

interface InspectionStatusBadgeProps {
  status: InspectionStatus;
  size?: 'sm' | 'md' | 'lg';
}

export default function InspectionStatusBadge({ status, size = 'md' }: InspectionStatusBadgeProps) {
  const getStatusColor = () => {
    switch (status) {
      case InspectionStatus.DRAFT:
        return 'bg-gray-100 text-gray-800 border-gray-300';
      case InspectionStatus.SUBMITTED:
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case InspectionStatus.APPROVED:
        return 'bg-green-100 text-green-800 border-green-300';
      case InspectionStatus.REJECTED:
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case InspectionStatus.DRAFT:
        return '📝';
      case InspectionStatus.SUBMITTED:
        return '⏳';
      case InspectionStatus.APPROVED:
        return '✅';
      case InspectionStatus.REJECTED:
        return '❌';
      default:
        return '•';
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
      default:
        return status;
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-medium ${getStatusColor()} ${
        sizeClasses[size]
      }`}
    >
      <span>{getStatusIcon()}</span>
      <span>{getStatusLabel()}</span>
    </span>
  );
}
