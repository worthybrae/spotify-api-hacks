// CollectionProgress.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { CollectionProgress } from '@/types/spotify';

interface CollectionProgressProps {
  hourlyProgress: CollectionProgress[];
}

export const CollectionProgressChart: React.FC<CollectionProgressProps> = ({ hourlyProgress }) => {
  const metrics = hourlyProgress.map((hour, index, array) => {
    const prevHour = index > 0 ? array[index - 1] : null;
    const hourlyRate = prevHour 
      ? hour.total_artists - prevHour.total_artists 
      : hour.artists_added;

    return {
      ...hour,
      hourlyRate
    };
  });

  return (
    <Card className="bg-white shadow-md">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-900">
          Collection Progress
          <span className="text-sm font-normal text-gray-500 ml-2">
            Hourly Progress & Rate
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-96 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={metrics}
              margin={{ top: 20, right: 50, bottom: 20, left: 50 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(timestamp) => {
                  const date = new Date(timestamp * 1000);
                  return date.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit'
                  });
                }}
                label={{ value: 'Time', position: 'bottom' }}
              />
              <YAxis
                yAxisId="left"
                orientation="left"
                label={{ 
                  value: 'Total Artists', 
                  angle: -90, 
                  position: 'insideLeft' 
                }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                label={{ 
                  value: 'Artists per Hour', 
                  angle: 90, 
                  position: 'insideRight' 
                }}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    const time = new Date(data.timestamp * 1000);
                    return (
                      <div className="bg-white p-3 border rounded shadow-lg">
                        <p className="font-semibold">
                          {time.toLocaleString()}
                        </p>
                        <p className="text-sm text-blue-600">
                          Total Artists: {data.total_artists.toLocaleString()}
                        </p>
                        <p className="text-sm text-orange-600">
                          Rate: {data.hourlyRate.toLocaleString()} artists/hour
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="total_artists"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="Total Artists"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="hourlyRate"
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
                name="Artists per Hour"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};