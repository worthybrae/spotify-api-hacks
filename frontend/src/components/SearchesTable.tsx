// SearchesTable.tsx
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Table, TableHeader, TableRow, TableCell, TableBody, TableHead } from "./ui/table";
import { RecentSearch } from "@/types/spotify";

  interface SearchesTableProps {
    searches: RecentSearch[];
  }
  
  export const SearchesTable: React.FC<SearchesTableProps> = ({ searches }) => (
    <Card className="bg-white shadow-md">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-900">Recently Completed Searches</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-gray-600">Query</TableHead>
                <TableHead className="text-gray-600">Artists Found</TableHead>
                <TableHead className="text-gray-600">Completed At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {searches.map((search, index) => (
                <TableRow key={index} className="hover:bg-gray-50">
                  <TableCell className="font-mono text-gray-900">{search.query}</TableCell>
                  <TableCell className="text-gray-900">{search.artists_found}</TableCell>
                  <TableCell className="text-gray-900">
                    {new Date(search.created_at).toLocaleTimeString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );