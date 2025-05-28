import React, { JSX, useState } from 'react';
import { ProcessedDiskData } from '@/components/metrics/disk/tabs/types';
import { formatBytes } from '@/components/metrics/disk/utils/formatters';
import { Card } from '@/design-system/components/Card/Card';
import { ProgressBar } from '@/design-system/components/ProgressBar/ProgressBar';
import { Table, TableColumn } from '@/design-system/components/Table/Table';
import { Badge } from '@/design-system/components/Badge/Badge';
import { Tabs, Tab, TabPanel } from '@/design-system/components/Tabs/Tabs';
import './DiskPartitionsTab.css';

interface DiskPartitionsTabProps {
  data: ProcessedDiskData;
  compact?: boolean;
}

const DiskPartitionsTab: React.FC<DiskPartitionsTabProps> = ({ data, compact = false }) => {
  const [activeTab, setActiveTab] = useState<'partitions' | 'physical'>('partitions');
  const [selectedPartition, setSelectedPartition] = useState<string | null>(null);
  const [selectedDisk, setSelectedDisk] = useState<string | null>(null);
  
  const { partitions, physicalDisks } = data;

  // Format health status
  const formatHealthStatus = (status: 'healthy' | 'warning' | 'error' | 'passed' | 'failed', id?: string): JSX.Element => {
    let color: string;
    let label: string;
    
    switch (status) {
      case 'healthy':
      case 'passed':
        color = 'var(--color-success)';
        label = 'Healthy';
        break;
      case 'warning':
        color = 'var(--color-warning)';
        label = 'Warning';
        break;
      case 'error':
      case 'failed':
        color = 'var(--color-danger)';
        label = 'Critical';
        break;
      default:
        color = 'var(--color-text-secondary)';
        label = 'Unknown';
    }
    
    // Using a key with the id ensures uniqueness even when the label is the same
    return <span key={`health-${id || Math.random().toString(36).substr(2, 9)}`} className="health-status" style={{ color }}>{label}</span>;
  };

  // Partition table columns
  const partitionColumns: TableColumn<any>[] = [
    {
      key: 'mountPoint',
      header: 'Mount Point',
      sortable: true,
      render: (partition) => (
        <div className="partition-mount">
          <span className="partition-mount__point">{partition.mountPoint}</span>
          <span className="partition-mount__device">{partition.device}</span>
        </div>
      )
    },
    {
      key: 'fsType',
      header: 'File System',
      sortable: true,
      render: (partition) => partition.fsType ? partition.fsType.toUpperCase() : ''
    },
    {
      key: 'percentUsed',
      header: 'Usage',
      sortable: true,
      render: (partition) => (
        <div className="partition-usage">
          <ProgressBar 
            value={partition.percentUsed} 
            label={`${partition.percentUsed.toFixed(1)}%`}
          />
          <div className="partition-usage__stats">
            <span>{formatBytes(partition.used)} of {formatBytes(partition.total)}</span>
          </div>
        </div>
      )
    },
    {
      key: 'total',
      header: 'Size',
      sortable: true,
      render: (partition) => formatBytes(partition.total)
    },
    {
      key: 'inodeUsage',
      header: 'Inodes',
      sortable: true,
      render: (partition) => `${partition.inodeUsage}%`
    },
    {
      key: 'health',
      header: 'Health',
      sortable: true,
      render: (partition) => formatHealthStatus(partition.health.status, partition.mountPoint)
    },
    {
      key: 'readOnly',
      header: 'Access',
      sortable: true,
      render: (partition) => (
        <Badge type={partition.readOnly ? 'warning' : 'success'}>
          {partition.readOnly ? 'Read-Only' : 'Read/Write'}
        </Badge>
      )
    }
  ];

  // Physical disk table columns
  const diskColumns: TableColumn<any>[] = [
    {
      key: 'model',
      header: 'Model',
      sortable: true
    },
    {
      key: 'type',
      header: 'Type',
      sortable: true,
      render: (disk) => disk.type.toUpperCase()
    },
    {
      key: 'size',
      header: 'Size',
      sortable: true,
      render: (disk) => formatBytes(disk.size)
    },
    {
      key: 'temperature',
      header: 'Temp',
      sortable: true,
      render: (disk) => (
        <div className="disk-temp">
          <span className={`disk-temp__value ${
            disk.temperature > 70 ? 'text-danger' :
            disk.temperature > 60 ? 'text-warning' : ''
          }`}>
            {disk.temperature}°C
          </span>
        </div>
      )
    },
    {
      key: 'health',
      header: 'Health',
      sortable: true,
      render: (disk) => (
        <div className="disk-health">
          {formatHealthStatus(disk.health.status, disk.id)}
          {disk.health.issues.length > 0 && (
            <Badge type="warning" className="ml-1">{disk.health.issues.length}</Badge>
          )}
        </div>
      )
    },
    {
      key: 'health.lifeRemaining',
      header: 'Life',
      sortable: true,
      render: (disk) => (
        <div className="disk-life">
          <ProgressBar 
            value={disk.health ? disk.health.lifeRemaining : 0} 
            label={`${disk.health ? disk.health.lifeRemaining : 0}%`}
          />
          <span className="disk-life__value">{disk.health ? disk.health.lifeRemaining : 0}%</span>
        </div>
      )
    },
    {
      key: 'partitions',
      header: 'Partitions',
      sortable: false,
      render: (disk) => disk.partitions.length
    }
  ];

  // Render compact view for dashboard
  if (compact) {
    return (
      <Card className="disk-partitions disk-partitions--compact">
        <div className="disk-partitions__header">
          <h3>Disk Usage</h3>
          <div className="disk-partitions__tabs">
            <Tabs activeTab={activeTab} onChange={(tabId: string) => setActiveTab(tabId as 'partitions' | 'physical')}>
              <Tab id="partitions" label="Partitions" children={null} />
              <Tab id="physical" label="Physical Disks" children={null} />
            </Tabs>
          </div>
        </div>

        <div className="disk-partitions__content">
          {activeTab === 'partitions' ? (
            <Table
              columns={partitionColumns}
              data={partitions.items}
              onRowClick={(partition) => setSelectedPartition(partition.uniqueId)}
              rowKey="uniqueId"
            />
          ) : (
            <Table
              columns={diskColumns}
              data={physicalDisks.items}
              onRowClick={(disk) => setSelectedDisk(disk.id)}
              rowKey="id"
            />
          )}
        </div>
      </Card>
    );
  }

  // Full view
  return (
    <div className="disk-partitions">
      <div className="disk-partitions__header">
        <div className="disk-summary">
          <h2>Disk Usage</h2>
          <div className="disk-summary__metrics">
            <div className="disk-summary__metric">
              <span className="disk-summary__label">Total Partitions:</span>
              <span className="disk-summary__value">{partitions.items.length}</span>
            </div>
            <div className="disk-summary__metric">
              <span className="disk-summary__label">Total Disks:</span>
              <span className="disk-summary__value">{physicalDisks.items.length}</span>
            </div>
          </div>
        </div>
        <div className="disk-partitions__tabs">
          <Tabs activeTab={activeTab} onChange={(tabId: string) => setActiveTab(tabId as 'partitions' | 'physical')}>
            <Tab id="partitions" label="Partitions" children={null} />
            <Tab id="physical" label="Physical Disks" children={null} />
          </Tabs>
        </div>
      </div>

      <div className="disk-partitions__content">
        <TabPanel id="partitions" active={activeTab === 'partitions'}>
          <div className="disk-partitions__table-container">
            <Table
              columns={partitionColumns}
              data={partitions.items}
              onRowClick={(partition) => setSelectedPartition(partition.uniqueId)}
              rowKey="uniqueId"
            />
          </div>

          {selectedPartition && (
            <div className="partition-details">
              <h3>Partition Details: {partitions.items.find(p => p.uniqueId === selectedPartition)?.mountPoint || selectedPartition}</h3>
              <div className="partition-details__content">
                {(() => {
                  const partition = partitions.items.find(p => p.uniqueId === selectedPartition);
                  if (!partition) return <p>Partition not found</p>;
                  
                  return (
                    <div className="partition-details__grid">
                      <Card className="partition-usage">
                        <h4>Disk Usage</h4>
                        <div className="partition-usage__chart">
                          <ProgressBar 
                            value={partition.percentUsed} 
                            label={`${partition.percentUsed.toFixed(1)}%`}
                          />
                          <div className="partition-usage__stats">
                            <div className="partition-stat">
                              <span className="partition-stat__label">Used:</span>
                              <span className="partition-stat__value">{formatBytes(partition.used)}</span>
                            </div>
                            <div className="partition-stat">
                              <span className="partition-stat__label">Available:</span>
                              <span className="partition-stat__value">{formatBytes(partition.available)}</span>
                            </div>
                            <div className="partition-stat">
                              <span className="partition-stat__label">Total:</span>
                              <span className="partition-stat__value">{formatBytes(partition.total)}</span>
                            </div>
                          </div>
                        </div>
                      </Card>

                      <Card className="partition-filesystem">
                        <h4>Filesystem Information</h4>
                        <div className="partition-filesystem__details">
                          <div className="partition-detail">
                            <span className="partition-detail__label">Filesystem:</span>
                            <span className="partition-detail__value">{partition.fsType}</span>
                          </div>
                          <div className="partition-detail">
                            <span className="partition-detail__label">Type:</span>
                            <span className="partition-detail__value">{partition.fsType}</span>
                          </div>
                          <div className="partition-detail">
                            <span className="partition-detail__label">Block Size:</span>
                            <span className="partition-detail__value">{typeof partition.blockSize === 'number' ? formatBytes(partition.blockSize) : ''}</span>
                          </div>
                          <div className="partition-detail">
                            <span className="partition-detail__label">Inodes:</span>
                            <span className="partition-detail__value">
                              {typeof partition.inodeUsage === 'number' ? `${partition.inodeUsage}% used` : ''}
                            </span>
                          </div>
                        </div>
                      </Card>

                      <Card className="partition-physical-disk">
                        <h4>Physical Disk</h4>
                        {(() => {
                          const physicalDisk = physicalDisks.items.find(d => d.id === partition.physicalDiskId);
                          if (!physicalDisk) return <p>Physical disk information not available</p>;
                          
                          return (
                            <div className="physical-disk-details">
                              <div className="physical-disk-details__header">
                                <h5>{physicalDisk.model}</h5>
                                <div className="physical-disk-details__badges">
                                  <Badge type="info">{physicalDisk.type.toUpperCase()}</Badge>
                                  <Badge 
                                    type={
                                      'success'
                                    }
                                  >
                                    {formatHealthStatus(physicalDisk.health.status, physicalDisk.id)}
                                  </Badge>
                                </div>
                              </div>
                              
                              <div className="physical-disk-details__stats">
                                <div className="physical-disk-stat">
                                  <span className="physical-disk-stat__label">Size:</span>
                                  <span className="physical-disk-stat__value">{formatBytes(physicalDisk.size)}</span>
                                </div>
                                <div className="physical-disk-stat">
                                  <span className="physical-disk-stat__label">Temperature:</span>
                                  <span className={`physical-disk-stat__value ${
                                    physicalDisk.temperature > 70 ? 'text-danger' :
                                    physicalDisk.temperature > 60 ? 'text-warning' : ''
                                  }`}>
                                    {physicalDisk.temperature}°C
                                  </span>
                                </div>
                                <div className="physical-disk-stat">
                                  <span className="physical-disk-stat__label">Life Remaining:</span>
                                  <div className="physical-disk-stat__progress">
                                    <ProgressBar 
                                      value={physicalDisk.health ? physicalDisk.health.lifeRemaining : 0} 
                                      label={`${physicalDisk.health ? physicalDisk.health.lifeRemaining : 0}%`}
                                    />
                                  </div>
                                </div>
                              </div>
                              
                              {physicalDisk.health.issues.length > 0 && (
                                <div className="physical-disk-issues">
                                  <h5>Health Issues:</h5>
                                  <ul className="physical-disk-issues__list">
                                    {physicalDisk.health.issues.map((issue, index) => (
                                      <li key={index} className="physical-disk-issue">
                                        <Badge type="danger">!</Badge>
                                        <span>{issue}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          );
                        })()}
                      </Card>
                    </div>
                  );
                })()}
              </div>
            </div>
          )}
        </TabPanel>

        <TabPanel id="physical" active={activeTab === 'physical'}>
          <div className="disk-physical__table-container">
            <Table
              columns={diskColumns}
              data={physicalDisks.items}
              onRowClick={(disk) => setSelectedDisk(disk.id)}
              rowKey="id"
            />
          </div>

          {selectedDisk && (
            <div className="physical-disk-details">
              <h3>Disk Details</h3>
              <div className="physical-disk-details__content">
                {(() => {
                  const disk = physicalDisks.items.find(d => d.id === selectedDisk);
                  if (!disk) return <p>Disk not found</p>;
                  
                  const diskPartitions = partitions.items.filter(p => p.physicalDiskId === disk.id);
                  
                  return (
                    <div className="physical-disk-details__grid">
                      <Card className="disk-info">
                        <h4>Disk Information</h4>
                        <div className="disk-info__grid">
                          <div className="disk-info__item">
                            <span className="disk-info__label">Model:</span>
                            <span className="disk-info__value">{disk.model}</span>
                          </div>
                          <div className="disk-info__item">
                            <span className="disk-info__label">Type:</span>
                            <span className="disk-info__value">{disk.type.toUpperCase()}</span>
                          </div>
                          <div className="disk-info__item">
                            <span className="disk-info__label">Size:</span>
                            <span className="disk-info__value">{formatBytes(disk.size)}</span>
                          </div>
                          <div className="disk-info__item">
                            <span className="disk-info__label">Temperature:</span>
                            <span className={`disk-info__value ${
                              disk.temperature > 70 ? 'text-danger' :
                              disk.temperature > 60 ? 'text-warning' : ''
                            }`}>
                              {disk.temperature}°C
                            </span>
                          </div>
                          <div className="disk-info__item">
                            <span className="disk-info__label">Health:</span>
                            <span className="disk-info__value">
                              {formatHealthStatus(disk.health.status, disk.id)}
                              {disk.health.issues.length > 0 && (
                                <Badge type="warning" className="ml-1">{disk.health.issues.length}</Badge>
                              )}
                            </span>
                          </div>
                          <div className="disk-info__item">
                            <span className="disk-info__label">Life Remaining:</span>
                            <div className="disk-info__progress">
                              <ProgressBar 
                                value={disk.health.lifeRemaining}
                                label={`${disk.health.lifeRemaining}%`}
                              />
                              <span className="disk-info__progress-value">{disk.health.lifeRemaining}%</span>
                            </div>
                          </div>
                        </div>
                      </Card>

                      {disk.health.issues.length > 0 && (
                        <Card className="disk-health-issues">
                          <h4>Health Issues</h4>
                          <ul className="disk-health-issues__list">
                            {disk.health.issues.map((issue, index) => (
                              <li key={index} className="disk-health-issue">
                                <Badge type="danger">!</Badge>
                                <span>{issue}</span>
                              </li>
                            ))}
                          </ul>
                        </Card>
                      )}

                      <Card className="disk-partitions">
                        <h4>Partitions</h4>
                        {diskPartitions.length > 0 ? (
                          <div className="disk-partitions__list">
                            {diskPartitions.map(partition => (
                              <div key={partition.mountPoint} className="disk-partition">
                                <div className="disk-partition__header">
                                  <span className="disk-partition__mount">{partition.mountPoint}</span>
                                  <span className="disk-partition__device">{partition.device}</span>
                                </div>
                                <div className="disk-partition__usage">
                                  <div className="disk-partition__usage-info">
                                    <span className="disk-partition__usage-percent">
                                      {partition.percentUsed.toFixed(1)}%
                                    </span>
                                    <span className="disk-partition__usage-stats">
                                      {formatBytes(partition.used)} of {formatBytes(partition.total)}
                                    </span>
                                  </div>
                                  <ProgressBar 
                                    value={partition.percentUsed}
                                  />
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p>No partitions found on this disk</p>
                        )}
                      </Card>
                    </div>
                  );
                })()}
              </div>
            </div>
          )}
        </TabPanel>
      </div>
    </div>
  );
};

export default DiskPartitionsTab;
