import React from 'react';

export interface TableColumn {
  id: string;
  label: string;
  render?: (row: any, rowIndex: number) => React.ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
}

interface TableProps {
  columns: TableColumn[];
  data: any[];
  onRowClick?: (row: any, index: number) => void;
  selectedRow?: any;
  emptyMessage?: string;
  maxHeight?: string;
  isLoading?: boolean;
  sortable?: boolean;
}

export const Table: React.FC<TableProps> = ({
  columns,
  data,
  onRowClick,
  selectedRow,
  emptyMessage = 'No data available',
  maxHeight,
  isLoading = false,
  sortable = true,
}) => {
  return (
    <div className="table-container" style={{ maxHeight }}>
      <table className="system-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th 
                key={column.id} 
                style={{ width: column.width }}
                className={`${column.align ? `text-${column.align}` : ''} ${column.sortable && sortable ? 'sortable' : ''}`}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan={columns.length} className="loading-cell">
                Loading data...
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="empty-cell">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick && onRowClick(row, rowIndex)}
                className={selectedRow === row ? 'selected-row' : ''}
              >
                {columns.map((column) => (
                  <td 
                    key={column.id} 
                    className={column.align ? `text-${column.align}` : ''}
                  >
                    {column.render ? column.render(row, rowIndex) : row[column.id]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};
