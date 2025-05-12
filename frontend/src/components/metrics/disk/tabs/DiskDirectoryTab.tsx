import React, { useState, useEffect } from 'react';
import { ProcessedDiskData } from '../types';
import { formatBytes } from '../utils/formatters';
import { Card } from '@/design-system/components/Card/Card';
import { Table, TableColumn } from '@/design-system/components/Table/Table';
import { Button } from '@/design-system/components/Button/Button';
import { SearchInput } from '@/components/common/SearchInput';
import { Treemap } from '@/components/common/Treemap';

// Directory item type from ProcessedDiskData
type DirectoryItem = {
  path: string;
  size: number;
  fileCount: number;
  lastModified: number;
  type: string;
  cleanable: boolean;
};

interface DiskDirectoryTabProps {
  data: ProcessedDiskData;
}

export const DiskDirectoryTab: React.FC<DiskDirectoryTabProps> = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [selectedCleanup, setSelectedCleanup] = useState<string | null>(null);
  
  // Get directories from data or use empty array as fallback
  const directories = data.directories?.largest || [];
  

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Filter directories based on search term
  const filteredDirectories = directories.filter((dir: DirectoryItem) =>
    dir.path.toLowerCase().includes(debouncedSearchTerm.toLowerCase())
  );
  
  // Transform directory data for Treemap
  const treemapData = {
    name: 'Root',
    value: directories.reduce((sum: number, dir: DirectoryItem) => sum + dir.size, 0),
    children: directories.map((dir: DirectoryItem) => ({
      name: dir.path.split('/').pop() || dir.path,
      path: dir.path,
      value: dir.size,
      fileCount: dir.fileCount,
      lastModified: dir.lastModified,
      type: dir.type,
      cleanable: dir.cleanable
    }))
  };

  // Get directory details for the selected path
  const selectedDirectory = selectedPath 
    ? directories.find((dir: DirectoryItem) => dir.path === selectedPath)
    : null;

  // Directory table columns
  const directoryColumns: TableColumn<DirectoryItem>[] = [
    {
      key: 'path',
      header: 'Path',
      sortable: true,
      render: (item: DirectoryItem) => {
        const name = item.path.split('/').pop() || item.path;
        return (
          <div className="directory-path">
            <span className="directory-path__name">{name}</span>
            {name !== item.path && (
              <span className="directory-path__full">{item.path}</span>
            )}
          </div>
        );
      }
    },
    {
      key: 'size',
      header: 'Size',
      sortable: true,
      render: (item: DirectoryItem) => formatBytes(item.size)
    },
    {
      key: 'fileCount',
      header: 'Files',
      sortable: true,
      render: (item: DirectoryItem) => item.fileCount.toLocaleString()
    },
    {
      key: 'lastModified',
      header: 'Last Modified',
      sortable: true,
      render: (item: DirectoryItem) => new Date(item.lastModified).toLocaleString()
    },
    {
      key: 'actions',
      header: 'Actions',
      sortable: false,
      render: (item: DirectoryItem) => (
        <div className="directory-actions">
          <Button
            size="sm"
            variant="secondary"
            outlined
            onClick={() => setSelectedPath(item.path)}
          >
            View Details
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setSelectedCleanup(item.path)}
          >
            Clean Up
          </Button>
        </div>
      )
    }
  ];

  return (
    <div className="disk-directory">
      <div className="disk-directory__header">
        <h2>Disk Usage by Directory</h2>
        <div className="disk-directory__search">
          <SearchInput 
            placeholder="Search directories..." 
            initialValue={searchTerm}
            onSearch={setSearchTerm}
          />
        </div>
      </div>

      <div className="disk-directory__content">
        <div className="disk-directory__treemap">
          <Card>
            <h3>Disk Usage Visualization</h3>
            <div className="treemap-container">
              <Treemap data={treemapData} />
            </div>
          </Card>
        </div>

        <div className="disk-directory__table">
          <Card>
            <h3>Directory List</h3>
            <Table<DirectoryItem>
              columns={directoryColumns}
              data={filteredDirectories}
              onRowClick={(dir) => setSelectedPath(dir.path)}
              rowKey="path"
            />
          </Card>
        </div>
      </div>

      {/* Directory Details Modal */}
      {selectedDirectory && (
        <div className="directory-details-modal">
          <div className="directory-details-modal__content">
            <div className="directory-details__header">
              <h3>{selectedDirectory.path.split('/').pop() || selectedDirectory.path}</h3>
              <Button 
                variant="secondary"
                circle
                size="sm"
                onClick={() => setSelectedPath(null)}
              >
                ×
              </Button>
            </div>
            
            <div className="directory-details__content">
              <div className="directory-details__info">
                <div className="info-row">
                  <span className="info-label">Path:</span>
                  <span className="info-value">{selectedDirectory.path}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Size:</span>
                  <span className="info-value">{formatBytes(selectedDirectory.size)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Files:</span>
                  <span className="info-value">{selectedDirectory.fileCount.toLocaleString()}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Last Modified:</span>
                  <span className="info-value">
                    {new Date(selectedDirectory.lastModified).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="directory-details__subdirectories">
                <h4>Directory Information</h4>
                <p>Type: {selectedDirectory.type}</p>
                <p>Path: {selectedDirectory.path}</p>
                <p>Cleanable: {selectedDirectory.cleanable ? 'Yes' : 'No'}</p>
                <p>Files: {selectedDirectory.fileCount.toLocaleString()}</p>
                <p>Size: {formatBytes(selectedDirectory.size)}</p>
              </div>

              <div className="directory-details__actions">
                <Button 
                  variant="secondary"
                  outlined
                  size="md"
                  onClick={() => setSelectedCleanup(selectedDirectory.path)}
                >
                  Clean Up Directory
                </Button>
                <Button 
                  variant="primary"
                  size="md"
                  onClick={() => console.log('Opening file explorer for', selectedDirectory.path)}
                >
                  Show in File Explorer
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cleanup Confirmation Modal */}
      {selectedCleanup && (
        <div className="cleanup-confirmation-modal">
          <div className="cleanup-confirmation-modal__content">
            <div className="cleanup-confirmation-modal__header">
              <h3>Confirm Cleanup</h3>
              <Button 
                variant="secondary"
                circle
                size="sm"
                onClick={() => setSelectedCleanup(null)}
              >
                ×
              </Button>
            </div>
            <div className="cleanup-confirmation-modal__body">
              <p>Are you sure you want to clean up this directory? This action cannot be undone.</p>
              {selectedCleanup && (
                <div className="cleanup-directory-info">
                  <p><strong>Directory:</strong> {selectedCleanup}</p>
                  <p><strong>Type:</strong> {directories.find((d: DirectoryItem) => d.path === selectedCleanup)?.type || 'Unknown'}</p>
                </div>
              )}
            </div>
            <div className="cleanup-confirmation-modal__actions">
              <Button 
                variant="secondary"
                outlined
                size="md"
                onClick={() => setSelectedCleanup(null)}
              >
                Cancel
              </Button>
              <Button 
                variant="danger"
                size="md"
                onClick={() => {
                  console.log('Cleanup confirmed for', selectedCleanup);
                  setSelectedCleanup(null);
                }}
              >
                Confirm Cleanup
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiskDirectoryTab;
