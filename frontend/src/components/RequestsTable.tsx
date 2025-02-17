// RequestsTable.tsx
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Table, TableHeader, TableRow, TableCell, TableBody, TableHead } from "./ui/table";
import { WindowRequest } from '../types/spotify';

interface RequestsTableProps {
  requests: WindowRequest[];
  windowStart: number;
}
  
  export const RequestsTable: React.FC<RequestsTableProps> = ({ requests, windowStart }) => (
    <Card className="bg-white shadow-md">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-900">Recent API Requests</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-gray-600">Time</TableHead>
                <TableHead className="text-gray-600">Query</TableHead>
                <TableHead className="text-gray-600">Offset</TableHead>
                <TableHead className="text-gray-600">Artists Found</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {requests
                .filter(req => req.timestamp >= windowStart)
                .map((request, index) => (
                  <TableRow key={index} className="hover:bg-gray-50">
                    <TableCell className="text-gray-900">
                      {new Date(request.timestamp * 1000).toLocaleTimeString()}
                    </TableCell>
                    <TableCell className="font-mono text-gray-900">{request.query}</TableCell>
                    <TableCell className="text-gray-900">{request.offset}</TableCell>
                    <TableCell className="text-gray-900">{request.artists_found}</TableCell>
                  </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );