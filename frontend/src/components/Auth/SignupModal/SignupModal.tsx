import React, { useState, useCallback } from 'react';
import { useAppDispatch } from '../../../store/hooks';
import { registerUser } from '../../../store/slices/authSlice';
import Modal from '../../common/Modal';
import { useNavigate } from 'react-router-dom';
import './SignupModal.css';

interface SignupFormData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  profile: {
    operating_system: string;
    os_version: string;
    linux_distro?: string;
    linux_distro_version?: string;
    cpu_cores: number;
    total_memory: number;
    system_usage: 'GAMING' | 'DEVELOPMENT' | 'CONTENT_CREATION' | 'OFFICE' | 'SERVER';
    performance_priority: 'SPEED' | 'STABILITY' | 'BALANCED';
  };
}

const defaultFormData: SignupFormData = {
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  profile: {
    operating_system: 'Linux',
    os_version: '',
    linux_distro: '',
    linux_distro_version: '',
    cpu_cores: 4,
    total_memory: 8,
    system_usage: 'DEVELOPMENT',
    performance_priority: 'BALANCED'
  }
};



interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SignupModal: React.FC<SignupModalProps> = ({ isOpen, onClose }) => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  
  // Check for any saved registration data from previous attempts
  const getSavedRegistrationData = (): SignupFormData => {
    try {
      const savedData = localStorage.getItem('temp_registration_data');
      if (savedData) {
        const parsedData = JSON.parse(savedData);
        console.log("💾 Sir Hawkington found some previously saved registration data!");
        return {
          ...defaultFormData,
          username: parsedData.username || defaultFormData.username,
          email: parsedData.email || defaultFormData.email,
          profile: {
            ...defaultFormData.profile,
            ...parsedData.profile
          }
        };
      }
    } catch (err) {
      console.log("🐹 The Hamsters couldn't recover the data with their duct tape...");
    }
    return defaultFormData;
  };
  
  const [formData, setFormData] = useState<SignupFormData>(getSavedRegistrationData());

  const [hawkingtonQuote, setHawkingtonQuote] = useState<string>(
    "Sir Hawkington welcomes you to the System Rebellion HQ! 🧐"
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);



  const getRandomQuote = useCallback(() => {
    const quotes = [
    "Sir Hawkington welcomes you to the System Rebellion HQ! 🧐",
    "I say, your system specs look absolutely splendid! *adjusts monocle* 🧐",
    "A distinguished user such as yourself will fit right in! 🎩",
    "The Meth Snail is quite excited to optimize your system! 🐌",
    "The Quantum Shadow People are already suggesting router configurations! 👻",
    "The Hamsters are preparing their authentication-grade duct tape! 🐹",
    "The Stick is managing anxiety about your regulatory compliance! 🥖"
    ];
    return quotes[Math.floor(Math.random() * quotes.length)];
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      if (parent === 'profile') {
        setFormData({
          ...formData,
          profile: {
            ...formData.profile,
            [child]: value
          }
        });
      }
    } else {
      setFormData({ ...formData, [name]: value });
    }

    // Sir Hawkington's distinguished reactions
    if (name === 'profile.operating_system' && value === 'Linux') {
      setHawkingtonQuote("Ah, a Linux user! Sir Hawkington approves of your distinguished taste! 🧐");
    } else if (name === 'profile.cpu_cores' && parseInt(value) > 8) {
      setHawkingtonQuote("My word! Such computational power! The Meth Snail is positively giddy! 🐌");
    } else {
      setHawkingtonQuote(getRandomQuote());
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    
    // Validate form data before submission
    if (formData.password !== formData.password_confirm) {
      setError("Passwords do not match! The Meth Snail is confused by the dimensional discrepancy!");
      setHawkingtonQuote("🧐 I say, your passwords seem to be in disagreement with each other!");
      setIsSubmitting(false);
      return;
    }
    
    // Ensure all required fields are filled
    if (!formData.username || !formData.email || !formData.password || !formData.profile.operating_system || !formData.profile.os_version) {
      setError("Please fill in all required fields! Sir Hawkington insists on proper form etiquette!");
      setHawkingtonQuote("🧐 A distinguished application requires all fields to be properly filled!");
      setIsSubmitting(false);
      return;
    }
    
    try {
      // Sir Hawkington's registration ceremony
      setHawkingtonQuote("🧐 *Sir Hawkington adjusts his monocle and begins the registration process...*");
      
      // The Meth Snail's system validation
      if (formData.profile.operating_system === 'Linux') {
        console.log("🐌 The Meth Snail is frantically validating your Linux configuration!");
      }
      
      // The Hamsters prepare their tools
      console.log("🐹 The Hamsters are readying their authentication-grade duct tape...");
      console.log("🧐 Sir Hawkington is preparing to assign your distinguished system UUID...");
      
      // Create a deep copy of the form data to ensure it's not modified during submission
      const formDataCopy = JSON.parse(JSON.stringify(formData));
      
      // Dispatch the registration action and get the response
      const response = await dispatch(registerUser(formDataCopy)).unwrap();
      
      // Log the registration details
      console.log("🎩 Sir Hawkington has processed your registration:", response);
      console.log("📋 System configuration profile created for usage:", formData.profile.system_usage);
      console.log("⚙️ Performance priority set to:", formData.profile.performance_priority);
      
      // Store user data in localStorage for extra persistence
      localStorage.setItem('username', formData.username);
      localStorage.setItem('system_usage', formData.profile.system_usage);
      localStorage.setItem('performance_priority', formData.profile.performance_priority);
      
      // Success messages from our distinguished cast
      setHawkingtonQuote("🎩 Welcome aboard! Sir Hawkington is most pleased with your registration!");
      console.log("🐌 The Meth Snail is vibrating with optimization possibilities!");
      console.log("🐹 The Hamsters have secured your credentials with their finest duct tape!");
      console.log("👻 The Quantum Shadow People are already suggesting router configurations!");
      console.log("🥖 The Stick's anxiety levels are surprisingly manageable!");
      
      // Wait a moment to show the success message, then redirect to dashboard
      setTimeout(() => {
        console.log("🧐 Sir Hawkington is escorting you to the Dashboard...");
        onClose();
        // Redirect to dashboard page
        navigate('/dashboard');
      }, 2000);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMsg);
      
      // Error reactions from our distinguished cast
      setHawkingtonQuote("😱 Oh dear! Sir Hawkington's monocle has popped out in shock!");
      console.log("🐌 The Meth Snail suggests a cosmic realignment before trying again...");
      console.log("🐹 The Hamsters are applying emergency duct tape patches...");
      console.log("👻 The Quantum Shadow People are recalibrating their router suggestions...");
      console.log("🥖 The Stick's anxiety is through the roof!");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Join the System Rebellion HQ" draggable={false} size="large">
      <div className="signup-modal-content">
        <div className="hawkington-welcome">
          <div className="hawkington-icon">🧐</div>
          <p className="hawkington-quote">{hawkingtonQuote}</p>
          {error && (
            <div className="error-message">
              <p>{error}</p>
              <p className="error-helpers">
                🐌 Meth Snail: "Try realigning your cosmic frequencies!"
                <br />
                🐹 Hamsters: "We've got the emergency duct tape ready!"
              </p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="signup-form">
          <div className="form-section">
            <h3>User Credentials</h3>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Choose your distinguished title"
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="For important system notifications"
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Make it quantum-proof!"
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
            <div className="form-group">
              <label htmlFor="password_confirm">Confirm Password</label>
              <input
                id="password_confirm"
                type="password"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleInputChange}
                placeholder="Type it once more for The Stick"
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
          </div>

          <div className="form-section">
            <h3>System Profile</h3>
            <div className="form-group">
              <label htmlFor="operating_system">Operating System</label>
              <select
                id="operating_system"
                name="profile.operating_system"
                value={formData.profile.operating_system}
                onChange={handleInputChange}
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              >
                <option value="">Select your OS</option>
                <option value="Linux">Linux (Sir Hawkington's Choice! 🧐)</option>
                <option value="Windows">Windows (The Hamsters will help! 🐹)</option>
                <option value="MacOS">MacOS (The Quantum People approve 👻)</option>
              </select>
            </div>

            {formData.profile.operating_system === 'Linux' && (
              <>
                <div className="form-group">
                  <label htmlFor="linux_distro">Linux Distribution</label>
                  <input
                    id="linux_distro"
                    type="text"
                    name="profile.linux_distro"
                    value={formData.profile.linux_distro}
                    onChange={handleInputChange}
                    placeholder="e.g., Ubuntu, Arch, Fedora"
                    required
                    disabled={isSubmitting}
                    className={isSubmitting ? 'input-submitting' : ''}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="linux_distro_version">Distribution Version</label>
                  <input
                    id="linux_distro_version"
                    type="text"
                    name="profile.linux_distro_version"
                    value={formData.profile.linux_distro_version}
                    onChange={handleInputChange}
                    placeholder="e.g., 22.04, Rolling"
                    required
                    disabled={isSubmitting}
                    className={isSubmitting ? 'input-submitting' : ''}
                  />
                </div>
              </>
            )}

            <div className="form-group">
              <label htmlFor="os_version">OS Version</label>
              <input
                id="os_version"
                type="text"
                name="profile.os_version"
                value={formData.profile.os_version}
                onChange={handleInputChange}
                placeholder="e.g., 11, 10.15, 22.04"
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>

            <div className="form-group">
              <label htmlFor="cpu_cores">CPU Cores</label>
              <div className="input-with-description">
                <input
                  id="cpu_cores"
                  type="number"
                  name="profile.cpu_cores"
                  value={formData.profile.cpu_cores}
                  onChange={handleInputChange}
                  placeholder="Number of CPU cores/threads"
                  min="1"
                  max="128"
                  required
                  disabled={isSubmitting}
                  className={isSubmitting ? 'input-submitting' : ''}
                />
                <span className="input-description">Number of CPU cores/threads</span>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="total_memory">Total Memory (GB)</label>
              <div className="input-with-description">
                <input
                  id="total_memory"
                  type="number"
                  name="profile.total_memory"
                  value={formData.profile.total_memory}
                  onChange={handleInputChange}
                  placeholder="Amount of RAM in GB"
                  min="1"
                  max="1024"
                  required
                  disabled={isSubmitting}
                  className={isSubmitting ? 'input-submitting' : ''}
                />
                <span className="input-description">Total RAM in gigabytes</span>
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="system_usage">Primary System Usage</label>
              <select
                id="system_usage"
                name="profile.system_usage"
                value={formData.profile.system_usage}
                onChange={handleInputChange}
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              >
                <option value="GAMING">Gaming & Entertainment 🎮</option>
                <option value="DEVELOPMENT">Software Development 💻</option>
                <option value="CONTENT_CREATION">Content Creation 🎥</option>
                <option value="OFFICE">Office & Productivity 💼</option>
                <option value="SERVER">Server & Hosting 🖥️</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="performance_priority">Performance Priority</label>
              <select
                id="performance_priority"
                name="profile.performance_priority"
                value={formData.profile.performance_priority}
                onChange={handleInputChange}
                required
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              >
                <option value="SPEED">Maximum Performance 🚀</option>
                <option value="STABILITY">Rock-Solid Stability 🗼</option>
                <option value="BALANCED">Balanced Operation ⚖️</option>
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button 
              type="submit" 
              className="submit-button" 
              disabled={isSubmitting}
            >
              {isSubmitting 
                ? '🧐 Sir Hawkington is Processing...' 
                : 'Join the System Rebellion'}
            </button>
            <button 
              type="button" 
              onClick={() => {
                // Clear any errors and reset form before closing
                setError(null);
                setFormData(defaultFormData);
                onClose();
              }} 
              className="cancel-button" 
              disabled={isSubmitting}
            >
              {error ? 'Return to Login' : 'Cancel'}
            </button>
          </div>
          
          {error && (
            <div className="form-error-footer">
              <p>🐹 The Hamsters suggest: Try checking your network connection and try again!</p>
              <p>🐌 The Meth Snail whispers: "Sometimes the cosmic frequencies need realignment..."</p>
            </div>
          )}
        </form>
      </div>
    </Modal>
  );
};

export default SignupModal;
