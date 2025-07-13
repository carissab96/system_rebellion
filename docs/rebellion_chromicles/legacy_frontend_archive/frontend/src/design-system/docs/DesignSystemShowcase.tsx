import React, { useState } from 'react';
import './DesignSystemShowcase.css';
import { 
  Button, 
  Card, 
  Alert, 
  Badge, 
  MetricsCard,
  Toggle,
  Input,
  ButtonVariant,
  CardVariant,
  AlertVariant,
  BadgeVariant,
  ToggleVariant,
  InputVariant
} from '../components';

/**
 * Design System Showcase Component
 * 
 * A component that showcases all available components in the Rebellion UI design system.
 * This serves as both documentation and a testing ground for the design system.
 */
export const DesignSystemShowcase: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [toggleStates, setToggleStates] = useState<Record<string, boolean>>({
    primary: true,
    secondary: false,
    accent: true,
    cyber: false,
    disabled: false,
    glow: true
  });
  
  // Sample data for metrics card
  const sampleMetricsData = {
    cpu: {
      title: 'CPU Usage',
      value: 42,
      unit: '%',
      previousValue: 38,
      changePercentage: 10.5,
      status: 'normal' as const,
      trend: 'up' as const,
      lastUpdated: '2 min ago',
      sparklineData: [20, 25, 30, 35, 28, 40, 42]
    },
    memory: {
      title: 'Memory',
      value: 6.2,
      unit: 'GB',
      previousValue: 5.8,
      changePercentage: 6.9,
      status: 'warning' as const,
      trend: 'up' as const,
      lastUpdated: '2 min ago',
      sparklineData: [30, 35, 40, 45, 50, 55, 60]
    },
    disk: {
      title: 'Disk I/O',
      value: 12.5,
      unit: 'MB/s',
      previousValue: 15.8,
      changePercentage: -20.9,
      status: 'optimized' as const,
      trend: 'down' as const,
      lastUpdated: '2 min ago',
      sparklineData: [60, 50, 40, 30, 20, 15, 12]
    },
    network: {
      title: 'Network',
      value: 87.3,
      unit: 'Mbps',
      previousValue: 45.2,
      changePercentage: 93.1,
      status: 'critical' as const,
      trend: 'up' as const,
      lastUpdated: '2 min ago',
      sparklineData: [20, 30, 40, 60, 70, 80, 87]
    }
  };

  // Button variants for showcase
  const buttonVariants: ButtonVariant[] = [
    'primary', 'secondary', 'accent', 'success', 'warning', 'danger', 'cyber'
  ];
  
  // Card variants for showcase
  const cardVariants: CardVariant[] = [
    'default', 'primary', 'secondary', 'accent', 'cyber'
  ];
  
  // Alert variants for showcase
  const alertVariants: AlertVariant[] = [
    'info', 'success', 'warning', 'danger', 'cyber'
  ];
  
  // Badge variants for showcase
  const badgeVariants: BadgeVariant[] = [
    'primary', 'secondary', 'accent', 'success', 'warning', 'danger', 'cyber', 'info'
  ];
  
  // Toggle variants for showcase
  const toggleVariants: ToggleVariant[] = [
    'primary', 'secondary', 'accent', 'success', 'warning', 'danger', 'cyber'
  ];
  
  // Input variants for showcase
  const inputVariants: InputVariant[] = [
    'primary', 'secondary', 'accent', 'cyber'
  ];

  return (
    <div className="design-system-showcase">
      <header className="showcase-header">
        <h1>Rebellion UI Design System</h1>
        <p>A proprietary design system for System Rebellion</p>
      </header>
      
      <nav className="showcase-nav">
        <button 
          className={`showcase-nav-item ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`showcase-nav-item ${activeTab === 'buttons' ? 'active' : ''}`}
          onClick={() => setActiveTab('buttons')}
        >
          Buttons
        </button>
        <button 
          className={`showcase-nav-item ${activeTab === 'cards' ? 'active' : ''}`}
          onClick={() => setActiveTab('cards')}
        >
          Cards
        </button>
        <button 
          className={`showcase-nav-item ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          Alerts
        </button>
        <button 
          className={`showcase-nav-item ${activeTab === 'badges' ? 'active' : ''}`}
          onClick={() => setActiveTab('badges')}
        >
          Badges
        </button>
        <button 
          className={`showcase-nav-item ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Metrics
        </button>
        <button 
          className={`showcase-nav-item ${activeTab === 'toggles' ? 'active' : ''}`}
          onClick={() => setActiveTab('toggles')}
        >
          Toggles
        </button>
        <button 
          className={`showcase-nav-item ${activeTab === 'inputs' ? 'active' : ''}`}
          onClick={() => setActiveTab('inputs')}
        >
          Inputs
        </button>
      </nav>
      
      <main className="showcase-content">
        {activeTab === 'overview' && (
          <section className="showcase-section">
            <h2>Rebellion UI Design System</h2>
            <p>
              A proprietary design system for System Rebellion that implements our cyberpunk aesthetic
              while maintaining accessibility and usability.
            </p>
            
            <h3>Design Principles</h3>
            <ul>
              <li><strong>Cyberpunk Aesthetic:</strong> Neon colors, gradients, and futuristic elements</li>
              <li><strong>Accessibility:</strong> High contrast, clear typography, and intuitive interactions</li>
              <li><strong>Consistency:</strong> Unified look and feel across all components</li>
              <li><strong>Flexibility:</strong> Customizable components that adapt to different contexts</li>
            </ul>
            
            <h3>Core Components</h3>
            <div className="overview-components">
              <div className="overview-component">
                <Button variant="primary">Button</Button>
                <span>Buttons</span>
              </div>
              <div className="overview-component">
                <Card className="overview-card">Card Component</Card>
                <span>Cards</span>
              </div>
              <div className="overview-component">
                <Alert variant="info">Alert Component</Alert>
                <span>Alerts</span>
              </div>
              <div className="overview-component">
                <Badge variant="cyber">Badge</Badge>
                <span>Badges</span>
              </div>
              <div className="overview-component">
                <div className="overview-metrics">
                  <MetricsCard
                    title="CPU"
                    value={42}
                    unit="%"
                    status="normal"
                  />
                </div>
                <span>Metrics</span>
              </div>
              <div className="overview-component">
                <Toggle
                  checked={true}
                  onChange={() => {}}
                  variant="cyber"
                />
                <span>Toggles</span>
              </div>
              <div className="overview-component">
                <div className="overview-input">
                  <Input
                    placeholder="Input"
                    variant="cyber"
                  />
                </div>
                <span>Inputs</span>
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'buttons' && (
          <section className="showcase-section">
            <h2>Buttons</h2>
            <p>
              Buttons are used to trigger actions or navigate between pages.
              They come in different variants, sizes, and states.
            </p>
            
            <h3>Button Variants</h3>
            <div className="component-demo">
              {buttonVariants.map(variant => (
                <div key={variant} className="component-demo-item">
                  <Button variant={variant}>{variant}</Button>
                  <code>{`<Button variant="${variant}">${variant}</Button>`}</code>
                </div>
              ))}
            </div>
            
            <h3>Button Sizes</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Button variant="primary" size="sm">Small</Button>
                <code>{`<Button variant="primary" size="sm">Small</Button>`}</code>
              </div>
              <div className="component-demo-item">
                <Button variant="primary" size="md">Medium</Button>
                <code>{`<Button variant="primary" size="md">Medium</Button>`}</code>
              </div>
              <div className="component-demo-item">
                <Button variant="primary" size="lg">Large</Button>
                <code>{`<Button variant="primary" size="lg">Large</Button>`}</code>
              </div>
            </div>
            
            <h3>Button Styles</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Button variant="primary" outlined>Outlined</Button>
                <code>{`<Button variant="primary" outlined>Outlined</Button>`}</code>
              </div>
              <div className="component-demo-item">
                <Button variant="accent" glow>Glow</Button>
                <code>{`<Button variant="accent" glow>Glow</Button>`}</code>
              </div>
              <div className="component-demo-item">
                <Button variant="cyber" circle>⚡</Button>
                <code>{`<Button variant="cyber" circle>⚡</Button>`}</code>
              </div>
            </div>
            
            <h3>Button States</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Button variant="primary" disabled>Disabled</Button>
                <code>{`<Button variant="primary" disabled>Disabled</Button>`}</code>
              </div>
              <div className="component-demo-item">
                <Button variant="primary" loading>Loading</Button>
                <code>{`<Button variant="primary" loading>Loading</Button>`}</code>
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'cards' && (
          <section className="showcase-section">
            <h2>Cards</h2>
            <p>
              Cards are used to group related content and actions.
              They come in different variants, elevations, and styles.
            </p>
            
            <h3>Card Variants</h3>
            <div className="component-demo cards-demo">
              {cardVariants.map(variant => (
                <div key={variant} className="component-demo-item">
                  <Card variant={variant} className="demo-card">
                    <h3>{variant} Card</h3>
                    <p>This is a {variant} card component.</p>
                  </Card>
                  <code>{`<Card variant="${variant}">Content</Card>`}</code>
                </div>
              ))}
            </div>
            
            <h3>Card Elevations</h3>
            <div className="component-demo cards-demo">
              <div className="component-demo-item">
                <Card elevation="flat" className="demo-card">
                  <h3>Flat Elevation</h3>
                  <p>No shadow</p>
                </Card>
                <code>{`<Card elevation="flat">Content</Card>`}</code>
              </div>
              <div className="component-demo-item">
                <Card elevation="low" className="demo-card">
                  <h3>Low Elevation</h3>
                  <p>Subtle shadow</p>
                </Card>
                <code>{`<Card elevation="low">Content</Card>`}</code>
              </div>
              <div className="component-demo-item">
                <Card elevation="medium" className="demo-card">
                  <h3>Medium Elevation</h3>
                  <p>Medium shadow</p>
                </Card>
                <code>{`<Card elevation="medium">Content</Card>`}</code>
              </div>
              <div className="component-demo-item">
                <Card elevation="high" className="demo-card">
                  <h3>High Elevation</h3>
                  <p>Prominent shadow</p>
                </Card>
                <code>{`<Card elevation="high">Content</Card>`}</code>
              </div>
            </div>
            
            <h3>Card Styles</h3>
            <div className="component-demo cards-demo">
              <div className="component-demo-item">
                <Card bordered className="demo-card">
                  <h3>Bordered Card</h3>
                  <p>With border</p>
                </Card>
                <code>{`<Card bordered>Content</Card>`}</code>
              </div>
              <div className="component-demo-item">
                <Card gradientBorder className="demo-card">
                  <h3>Gradient Border</h3>
                  <p>With gradient border</p>
                </Card>
                <code>{`<Card gradientBorder>Content</Card>`}</code>
              </div>
              <div className="component-demo-item">
                <Card glow className="demo-card">
                  <h3>Glow Effect</h3>
                  <p>With shadow glow</p>
                </Card>
                <code>{`<Card glow>Content</Card>`}</code>
              </div>
              <div className="component-demo-item">
                <Card glass className="demo-card">
                  <h3>Glass Effect</h3>
                  <p>With backdrop blur</p>
                </Card>
                <code>{`<Card glass>Content</Card>`}</code>
              </div>
            </div>
            
            <h3>Card with Sections</h3>
            <div className="component-demo cards-demo">
              <div className="component-demo-item">
                <Card 
                  className="demo-card"
                  header={<h3>Card Header</h3>}
                  footer={<div>Card Footer</div>}
                >
                  <p>Card body content</p>
                </Card>
                <code>{`<Card header={<h3>Header</h3>} footer={<div>Footer</div>}>Content</Card>`}</code>
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'alerts' && (
          <section className="showcase-section">
            <h2>Alerts</h2>
            <p>
              Alerts are used to communicate status, feedback, or other important information.
              They come in different variants, sizes, and styles.
            </p>
            
            <h3>Alert Variants</h3>
            <div className="component-demo">
              {alertVariants.map(variant => (
                <div key={variant} className="component-demo-item">
                  <Alert 
                    variant={variant} 
                    title={`${variant.charAt(0).toUpperCase() + variant.slice(1)} Alert`}
                  >
                    This is a {variant} alert with important information.
                  </Alert>
                  <code>{`<Alert variant="${variant}" title="${variant} Alert">Content</Alert>`}</code>
                </div>
              ))}
            </div>
            
            <h3>Alert Sizes</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Alert variant="info" size="sm" title="Small Alert">
                  This is a small alert.
                </Alert>
                <code>{`<Alert variant="info" size="sm" title="Small Alert">Content</Alert>`}</code>
              </div>
              <div className="component-demo-item">
                <Alert variant="info" size="md" title="Medium Alert">
                  This is a medium alert.
                </Alert>
                <code>{`<Alert variant="info" size="md" title="Medium Alert">Content</Alert>`}</code>
              </div>
              <div className="component-demo-item">
                <Alert variant="info" size="lg" title="Large Alert">
                  This is a large alert.
                </Alert>
                <code>{`<Alert variant="info" size="lg" title="Large Alert">Content</Alert>`}</code>
              </div>
            </div>
            
            <h3>Alert Styles</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Alert variant="warning" bordered title="Bordered Alert">
                  This is a bordered alert.
                </Alert>
                <code>{`<Alert variant="warning" bordered title="Bordered Alert">Content</Alert>`}</code>
              </div>
              <div className="component-demo-item">
                <Alert variant="danger" glow title="Glow Alert">
                  This is an alert with glow effect.
                </Alert>
                <code>{`<Alert variant="danger" glow title="Glow Alert">Content</Alert>`}</code>
              </div>
            </div>
            
            <h3>Alert with Actions</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Alert 
                  variant="cyber" 
                  title="Actionable Alert"
                  actionable
                  actionText="Apply"
                  onAction={() => alert('Action clicked')}
                >
                  This is an alert with an action button.
                </Alert>
                <code>{`<Alert variant="cyber" title="Actionable Alert" actionable actionText="Apply" onAction={handleAction}>Content</Alert>`}</code>
              </div>
              <div className="component-demo-item">
                <Alert 
                  variant="info" 
                  title="Dismissible Alert"
                  dismissible
                  onDismiss={() => alert('Dismiss clicked')}
                >
                  This is a dismissible alert.
                </Alert>
                <code>{`<Alert variant="info" title="Dismissible Alert" dismissible onDismiss={handleDismiss}>Content</Alert>`}</code>
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'badges' && (
          <section className="showcase-section">
            <h2>Badges</h2>
            <p>
              Badges are used to highlight status, counts, or labels.
              They come in different variants, sizes, and styles.
            </p>
            
            <h3>Badge Variants</h3>
            <div className="component-demo">
              {badgeVariants.map(variant => (
                <div key={variant} className="component-demo-item">
                  <Badge variant={variant}>{variant}</Badge>
                  <code>{`<Badge variant="${variant}">${variant}</Badge>`}</code>
                </div>
              ))}
            </div>
            
            <h3>Badge Sizes</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Badge variant="primary" size="sm">Small</Badge>
                <code>{`<Badge variant="primary" size="sm">Small</Badge>`}</code>
              </div>
              <div className="component-demo-item">
                <Badge variant="primary" size="md">Medium</Badge>
                <code>{`<Badge variant="primary" size="md">Medium</Badge>`}</code>
              </div>
              <div className="component-demo-item">
                <Badge variant="primary" size="lg">Large</Badge>
                <code>{`<Badge variant="primary" size="lg">Large</Badge>`}</code>
              </div>
            </div>
            
            <h3>Badge Styles</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Badge variant="secondary" outlined>Outlined</Badge>
                <code>{`<Badge variant="secondary" outlined>Outlined</Badge>`}</code>
              </div>
              <div className="component-demo-item">
                <Badge variant="accent" rounded>Rounded</Badge>
                <code>{`<Badge variant="accent" rounded>Rounded</Badge>`}</code>
              </div>
              <div className="component-demo-item">
                <Badge variant="danger" glow>Glow</Badge>
                <code>{`<Badge variant="danger" glow>Glow</Badge>`}</code>
              </div>
              <div className="component-demo-item">
                <Badge variant="cyber" pulse>Pulse</Badge>
                <code>{`<Badge variant="cyber" pulse>Pulse</Badge>`}</code>
              </div>
            </div>
            
            <h3>Badge Use Cases</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <div className="badge-with-text">
                  <span>Notifications</span>
                  <Badge variant="danger" rounded>5</Badge>
                </div>
                <code>{`<Badge variant="danger" rounded>5</Badge>`}</code>
              </div>
              <div className="component-demo-item">
                <div className="badge-with-text">
                  <span>Status:</span>
                  <Badge variant="success" rounded>Online</Badge>
                </div>
                <code>{`<Badge variant="success" rounded>Online</Badge>`}</code>
              </div>
              <div className="component-demo-item">
                <div className="badge-with-text">
                  <span>Version:</span>
                  <Badge variant="info">v1.0.0</Badge>
                </div>
                <code>{`<Badge variant="info">v1.0.0</Badge>`}</code>
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'toggles' && (
          <section className="showcase-section">
            <h2>Toggles</h2>
            <p>
              Toggles are used for binary choices like on/off, enable/disable, or show/hide.
              They come in different variants, sizes, and styles.
            </p>
            
            <h3>Toggle Variants</h3>
            <div className="component-demo">
              {toggleVariants.map(variant => (
                <div key={variant} className="component-demo-item">
                  <Toggle
                    checked={toggleStates[variant] || false}
                    onChange={(checked) => setToggleStates(prev => ({ ...prev, [variant]: checked }))}
                    variant={variant}
                    label={variant}
                  />
                  <code>{`<Toggle checked={${toggleStates[variant] || false}} onChange={handleChange} variant="${variant}" label="${variant}" />`}</code>
                </div>
              ))}
            </div>
            
            <h3>Toggle Sizes</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Toggle
                  checked={toggleStates.primary}
                  onChange={(checked) => setToggleStates(prev => ({ ...prev, primary: checked }))}
                  variant="primary"
                  size="sm"
                  label="Small"
                />
                <code>{`<Toggle checked={true} onChange={handleChange} variant="primary" size="sm" label="Small" />`}</code>
              </div>
              <div className="component-demo-item">
                <Toggle
                  checked={toggleStates.primary}
                  onChange={(checked) => setToggleStates(prev => ({ ...prev, primary: checked }))}
                  variant="primary"
                  size="md"
                  label="Medium"
                />
                <code>{`<Toggle checked={true} onChange={handleChange} variant="primary" size="md" label="Medium" />`}</code>
              </div>
              <div className="component-demo-item">
                <Toggle
                  checked={toggleStates.primary}
                  onChange={(checked) => setToggleStates(prev => ({ ...prev, primary: checked }))}
                  variant="primary"
                  size="lg"
                  label="Large"
                />
                <code>{`<Toggle checked={true} onChange={handleChange} variant="primary" size="lg" label="Large" />`}</code>
              </div>
            </div>
            
            <h3>Toggle Styles</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Toggle
                  checked={toggleStates.glow}
                  onChange={(checked) => setToggleStates(prev => ({ ...prev, glow: checked }))}
                  variant="cyber"
                  glow
                  label="With Glow"
                />
                <code>{`<Toggle checked={true} onChange={handleChange} variant="cyber" glow label="With Glow" />`}</code>
              </div>
              <div className="component-demo-item">
                <Toggle
                  checked={toggleStates.accent}
                  onChange={(checked) => setToggleStates(prev => ({ ...prev, accent: checked }))}
                  variant="accent"
                  label="Label Right"
                  labelRight
                />
                <code>{`<Toggle checked={true} onChange={handleChange} variant="accent" label="Label Right" labelRight />`}</code>
              </div>
              <div className="component-demo-item">
                <Toggle
                  checked={toggleStates.secondary}
                  onChange={(checked) => setToggleStates(prev => ({ ...prev, secondary: checked }))}
                  variant="secondary"
                  label="Label Left"
                  labelRight={false}
                />
                <code>{`<Toggle checked={false} onChange={handleChange} variant="secondary" label="Label Left" labelRight={false} />`}</code>
              </div>
            </div>
            
            <h3>Toggle States</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Toggle
                  checked={toggleStates.disabled}
                  onChange={(checked) => setToggleStates(prev => ({ ...prev, disabled: checked }))}
                  variant="primary"
                  disabled
                  label="Disabled"
                />
                <code>{`<Toggle checked={false} onChange={handleChange} variant="primary" disabled label="Disabled" />`}</code>
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'inputs' && (
          <section className="showcase-section">
            <h2>Inputs</h2>
            <p>
              Inputs are used to collect user data and information.
              They come in different variants, sizes, and styles.
            </p>
            
            <h3>Input Variants</h3>
            <div className="component-demo">
              {inputVariants.map(variant => (
                <div key={variant} className="component-demo-item">
                  <Input
                    placeholder={`${variant} input`}
                    variant={variant}
                  />
                  <code>{`<Input placeholder="${variant} input" variant="${variant}" />`}</code>
                </div>
              ))}
            </div>
            
            <h3>Input Sizes</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Input
                  placeholder="Small input"
                  variant="primary"
                  size="sm"
                />
                <code>{`<Input placeholder="Small input" variant="primary" size="sm" />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="Medium input"
                  variant="primary"
                  size="md"
                />
                <code>{`<Input placeholder="Medium input" variant="primary" size="md" />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="Large input"
                  variant="primary"
                  size="lg"
                />
                <code>{`<Input placeholder="Large input" variant="primary" size="lg" />`}</code>
              </div>
            </div>
            
            <h3>Input Styles</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Input
                  placeholder="With label"
                  variant="primary"
                  label="Input Label"
                />
                <code>{`<Input placeholder="With label" variant="primary" label="Input Label" />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="With helper text"
                  variant="primary"
                  helperText="This is helper text"
                />
                <code>{`<Input placeholder="With helper text" variant="primary" helperText="This is helper text" />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="With error"
                  variant="primary"
                  error="This field is required"
                />
                <code>{`<Input placeholder="With error" variant="primary" error="This field is required" />`}</code>
              </div>
            </div>
            
            <h3>Input Features</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Input
                  placeholder="Glow effect"
                  variant="cyber"
                  glow
                />
                <code>{`<Input placeholder="Glow effect" variant="cyber" glow />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="Glass effect"
                  variant="accent"
                  glass
                />
                <code>{`<Input placeholder="Glass effect" variant="accent" glass />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="Cyber border"
                  variant="cyber"
                  cyberBorder
                />
                <code>{`<Input placeholder="Cyber border" variant="cyber" cyberBorder />`}</code>
              </div>
            </div>
            
            <h3>Input with Icons</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <Input
                  placeholder="Search..."
                  variant="primary"
                  startIcon={<span>🔍</span>}
                />
                <code>{`<Input placeholder="Search..." variant="primary" startIcon={<span>🔍</span>} />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="Enter email"
                  variant="primary"
                  endIcon={<span>✉️</span>}
                />
                <code>{`<Input placeholder="Enter email" variant="primary" endIcon={<span>✉️</span>} />`}</code>
              </div>
              <div className="component-demo-item">
                <Input
                  placeholder="Password"
                  type="password"
                  variant="primary"
                  startIcon={<span>🔒</span>}
                  endIcon={<span>👁️</span>}
                />
                <code>{`<Input placeholder="Password" type="password" variant="primary" startIcon={<span>🔒</span>} endIcon={<span>👁️</span>} />`}</code>
              </div>
            </div>
          </section>
        )}
        
        {activeTab === 'metrics' && (
          <section className="showcase-section">
            <h2>Metrics Cards</h2>
            <p>
              Metrics Cards are specialized components for displaying system metrics.
              They include status indicators, trend visualization, and optional sparklines.
            </p>
            
            <h3>Metrics Card Statuses</h3>
            <div className="component-demo metrics-demo">
              <div className="component-demo-item">
                <MetricsCard
                  {...sampleMetricsData.cpu}
                  showSparkline
                />
                <code>{`<MetricsCard title="CPU Usage" value={42} unit="%" status="normal" trend="up" showSparkline />`}</code>
              </div>
              <div className="component-demo-item">
                <MetricsCard
                  {...sampleMetricsData.memory}
                  showSparkline
                />
                <code>{`<MetricsCard title="Memory" value={6.2} unit="GB" status="warning" trend="up" showSparkline />`}</code>
              </div>
              <div className="component-demo-item">
                <MetricsCard
                  {...sampleMetricsData.disk}
                  showSparkline
                />
                <code>{`<MetricsCard title="Disk I/O" value={12.5} unit="MB/s" status="optimized" trend="down" showSparkline />`}</code>
              </div>
              <div className="component-demo-item">
                <MetricsCard
                  {...sampleMetricsData.network}
                  showSparkline
                />
                <code>{`<MetricsCard title="Network" value={87.3} unit="Mbps" status="critical" trend="up" showSparkline />`}</code>
              </div>
            </div>
            
            <h3>Metrics Card Features</h3>
            <div className="component-demo">
              <div className="component-demo-item">
                <MetricsCard
                  title="Basic Metric"
                  value={42}
                  unit="%"
                />
                <code>{`<MetricsCard title="Basic Metric" value={42} unit="%" />`}</code>
              </div>
              <div className="component-demo-item">
                <MetricsCard
                  title="With Trend"
                  value={42}
                  unit="%"
                  previousValue={38}
                  changePercentage={10.5}
                  trend="up"
                />
                <code>{`<MetricsCard title="With Trend" value={42} unit="%" previousValue={38} changePercentage={10.5} trend="up" />`}</code>
              </div>
              <div className="component-demo-item">
                <MetricsCard
                  title="With Sparkline"
                  value={42}
                  unit="%"
                  showSparkline
                  sparklineData={[20, 25, 30, 35, 28, 40, 42]}
                />
                <code>{`<MetricsCard title="With Sparkline" value={42} unit="%" showSparkline sparklineData={[20, 25, 30, 35, 28, 40, 42]} />`}</code>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
};

export default DesignSystemShowcase;
