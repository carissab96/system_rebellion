import React, { useState, useEffect } from 'react';
import './Tabs.css';

export interface TabProps {
  id: string;
  label: string;
  children: React.ReactNode;
}

export interface TabsProps {
  activeTab?: string;
  onChange?: (tabId: string) => void;
  children: React.ReactNode;
}

export interface TabPanelProps {
  id: string;
  active: boolean;
  children: React.ReactNode;
}

export const Tab: React.FC<TabProps> = ({ children }) => {
  return <>{children}</>;
};

export const TabPanel: React.FC<TabPanelProps> = ({ active, children }) => {
  if (!active) return null;
  return <div className="sr-tab-panel">{children}</div>;
};

export const Tabs: React.FC<TabsProps> = ({ activeTab: externalActiveTab, onChange, children }) => {
  // Get all tabs from children
  const tabs = React.Children.toArray(children).filter(
    (child) => React.isValidElement(child) && child.type === Tab
  ) as React.ReactElement<TabProps>[];
  
  // Set initial active tab
  const [internalActiveTab, setInternalActiveTab] = useState<string>(
    externalActiveTab || (tabs.length > 0 ? tabs[0].props.id : '')
  );
  
  // Sync with external active tab if provided
  useEffect(() => {
    if (externalActiveTab !== undefined) {
      setInternalActiveTab(externalActiveTab);
    }
  }, [externalActiveTab]);
  
  // Handle tab click
  const handleTabClick = (tabId: string) => {
    if (onChange) {
      onChange(tabId);
    } else {
      setInternalActiveTab(tabId);
    }
  };
  
  // Get current active tab
  const activeTabId = externalActiveTab !== undefined ? externalActiveTab : internalActiveTab;
  
  return (
    <div className="sr-tabs-container">
      <div className="sr-tabs-header">
        {tabs.map((tab) => (
          <button
            key={tab.props.id}
            className={`sr-tab ${activeTabId === tab.props.id ? 'active' : ''}`}
            onClick={() => handleTabClick(tab.props.id)}
            role="tab"
            aria-selected={activeTabId === tab.props.id}
            aria-controls={`panel-${tab.props.id}`}
            id={`tab-${tab.props.id}`}
          >
            {tab.props.label}
          </button>
        ))}
      </div>
      <div className="sr-tabs-content">
        {tabs.map((tab) => (
          <div
            key={tab.props.id}
            role="tabpanel"
            id={`panel-${tab.props.id}`}
            aria-labelledby={`tab-${tab.props.id}`}
            hidden={activeTabId !== tab.props.id}
          >
            {activeTabId === tab.props.id && tab.props.children}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tabs;
