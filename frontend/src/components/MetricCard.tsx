// MetricCard.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';

export interface MetricCardProps {
    title: string;
    value: string | number;
    description?: string;
    icon: LucideIcon;
    iconColor: string;
    progress?: number;
  }

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  description,
  icon: Icon,
  iconColor,
  progress
}) => (
  <Card className="bg-white shadow-md hover:shadow-lg transition-shadow">
    <CardHeader className="flex flex-row items-center justify-between pb-2">
      <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
      <Icon className={`h-4 w-4 text-${iconColor}`} />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold text-gray-900">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {description && (
        <p className="text-xs text-gray-500 mt-1">{description}</p>
      )}
      {progress !== undefined && (
        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
          <div 
            className="bg-orange-500 rounded-full h-1.5" 
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      )}
    </CardContent>
  </Card>
);