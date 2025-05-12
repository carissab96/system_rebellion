import React, { useState, useMemo } from 'react';
import './Table.css';

export interface TableColumn<T> {
  key: string;
  header: string | React.ReactNode;
  sortable?: boolean;
  render?: (item: T) => React.ReactNode;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
}

export interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  className?: string;
  rowKey?: keyof T | ((item: T) => string | number);
  emptyState?: React.ReactNode;
  loading?: boolean;
  loadingText?: string;
  sortConfig?: {
    key: string;
    direction: 'asc' | 'desc';
  };
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
}

export const Table = <T extends object>({
  columns,
  data,
  onRowClick,
  className = '',
  rowKey,
  emptyState = 'No data available',
  loading = false,
  loadingText = 'Loading...',
  sortConfig,
  onSort,
}: TableProps<T>) => {
  const [internalSortConfig, setInternalSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const handleSort = (key: string, sortable?: boolean) => {
    if (!sortable) return;
    
    const isAsc = (sortConfig?.key === key || internalSortConfig?.key === key) && 
                 (sortConfig?.direction === 'asc' || internalSortConfig?.direction === 'asc');
    const direction = isAsc ? 'desc' : 'asc';
    
    if (onSort) {
      onSort(key, direction);
    } else {
      setInternalSortConfig({ key, direction });
    }
  };

  const sortedData = useMemo(() => {
    if (!sortConfig && !internalSortConfig) return data;
    
    const config = sortConfig || internalSortConfig;
    if (!config) return data;
    
    return [...data].sort((a, b) => {
      const aValue = (a as any)[config.key];
      const bValue = (b as any)[config.key];
      
      if (aValue < bValue) return config.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return config.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig, internalSortConfig]);

  const getRowKey = (item: T, index: number): string | number => {
    if (rowKey) {
      return typeof rowKey === 'function' ? rowKey(item) : (item[rowKey] as string | number);
    }
    return index;
  };

  const renderSortIcon = (key: string, sortable?: boolean) => {
    if (!sortable) return null;
    
    const config = sortConfig || internalSortConfig;
    if (!config || config.key !== key) return '↕';
    
    return config.direction === 'asc' ? '↑' : '↓';
  };

  if (loading) {
    return (
      <div className={`table-loading ${className}`}>
        <div className="table-loading-spinner"></div>
        <div className="table-loading-text">{loadingText}</div>
      </div>
    );
  }

  if (data.length === 0) {
    return <div className={`table-empty ${className}`}>{emptyState}</div>;
  }

  return (
    <div className={`table-container ${className}`}>
      <table className="table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th 
                key={String(column.key)}
                style={{
                  width: column.width,
                  textAlign: column.align || 'left',
                  cursor: column.sortable ? 'pointer' : 'default'
                }}
                onClick={() => handleSort(String(column.key), column.sortable)}
              >
                <div className="table-header-content">
                  {column.header}
                  {column.sortable && (
                    <span className="sort-icon">
                      {renderSortIcon(String(column.key), column.sortable)}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((item, index) => (
            <tr 
              key={getRowKey(item, index)}
              onClick={() => onRowClick?.(item)}
              className={onRowClick ? 'clickable-row' : ''}
            >
              {columns.map((column) => (
                <td 
                  key={String(column.key)}
                  style={{ textAlign: column.align || 'left' }}
                >
                  {column.render ? column.render(item) : (item as any)[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
