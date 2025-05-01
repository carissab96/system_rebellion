import React, { useState, useRef, useEffect } from "react";
import { useAppSelector, useAppDispatch } from "../../../store/hooks";
import { updateProfile, checkAuthStatus } from "../../../store/slices/authSlice";
import { CharacterAvatarSelector, getCharacterById } from "../../common/CharacterIcons";
import "./UserProfile.css";

// Define extended profile interface
interface ExtendedProfile {
  profile: {
    operating_system: string;
    os_version: string;
    linux_distro: string;
    linux_distro_version: string;
    cpu_cores: number;
    total_memory: number;
    avatar: string;
    bio?: string;
    joined_date?: string;
  };
  preferences: {
    optimization_level: string;
    theme_preferences: {
      use_dark_mode: boolean;
    };
    notification_preferences?: {
      email_alerts: boolean;
      system_alerts: boolean;
    };
  };
  email?: string;
}

interface UserProfileProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ isOpen, onClose }) => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading, error } = useAppSelector(state => state.auth as { 
    user: ExtendedProfile & { username: string }, 
    isAuthenticated: boolean, 
    isLoading: boolean, 
    error: string | null 
  });
  
  const [localError, setLocalError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedAvatar, setSelectedAvatar] = useState<string>('sir-hawkington');
  const [activeTab, setActiveTab] = useState<'profile' | 'system' | 'preferences'>('profile');
  
  // Refs to store the edited values
  const bioRef = useRef<HTMLTextAreaElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);
  const osRef = useRef<HTMLInputElement>(null);
  const distroRef = useRef<HTMLInputElement>(null);
  const cpuCoresRef = useRef<HTMLInputElement>(null);
  const memoryRef = useRef<HTMLInputElement>(null);
  const optimizationLevelRef = useRef<HTMLSelectElement>(null);
  const emailAlertsRef = useRef<HTMLInputElement>(null);
  const systemAlertsRef = useRef<HTMLInputElement>(null);
  
  // Fetch user data when component mounts
  useEffect(() => {
    if (!user && isAuthenticated) {
      dispatch(checkAuthStatus());
    }
  }, [user, isAuthenticated, dispatch]);
  
  // Set the selected avatar when user data loads
  useEffect(() => {
    if (user?.profile?.avatar) {
      setSelectedAvatar(user.profile.avatar);
    }
  }, [user]);
  
  // Update error state when Redux error changes
  useEffect(() => {
    if (error) {
      setLocalError(error);
    }
  }, [error]);
  
  // Handle escape key press
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && onClose) {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscapeKey);
      return () => {
        document.removeEventListener('keydown', handleEscapeKey);
      };
    }
    return undefined;
  }, [isOpen, onClose]);
  
  // Handle avatar selection
  const handleAvatarSelect = (avatarId: string) => {
    setSelectedAvatar(avatarId);
    console.log(`🧐 Sir Hawkington: "Ah, I see you've chosen ${avatarId} as your digital persona. Splendid choice!"`);
  };
  
  // Handle edit/save button click
  const handleEditClick = async () => {
    if (!isAuthenticated) {
      console.log("Error: You must be logged in to edit your profile");
      setLocalError("You must be logged in to edit your profile");
      return;
    }
    
    if (isEditing) {
      console.log("Saving profile changes...");
      try {
        // Get values from refs based on active tab
        let profileData: Record<string, any> = {};
        let preferencesData: Record<string, any> = {};
        
        // Always include avatar
        profileData.avatar = selectedAvatar;
        
        // Profile tab data
        if (bioRef.current) {
          profileData.bio = bioRef.current.value.trim().substring(0, 300); // Limit to 300 chars
        }
        
        if (emailRef.current) {
          profileData.email = emailRef.current.value;
        }
        
        // System tab data
        if (activeTab === 'system' || activeTab === 'profile') {
          const osValue = osRef.current?.value || '';
          const distroValue = distroRef.current?.value || '';
          const cpuCores = Number(cpuCoresRef.current?.value || 0);
          const memory = Number(memoryRef.current?.value || 0) * 1024; // Convert GB to MB
          
          // Split OS and distro
          const osParts = osValue.split(' ');
          const osName = osParts[0] || '';
          const osVersion = osParts.slice(1).join(' ') || '';
          
          const distroParts = distroValue.split(' ');
          const distroName = distroParts[0] || '';
          const distroVersion = distroParts.slice(1).join(' ') || '';
          
          // Add to profile data
          profileData.operating_system = osName;
          profileData.os_version = osVersion;
          profileData.linux_distro = distroName;
          profileData.linux_distro_version = distroVersion;
          profileData.cpu_cores = cpuCores;
          profileData.total_memory = memory;
        }
        
        // Preferences tab data
        if (activeTab === 'preferences' || activeTab === 'profile') {
          const optimizationLevel = optimizationLevelRef.current?.value || 'moderate';
          const emailAlerts = emailAlertsRef.current?.checked || false;
          const systemAlerts = systemAlertsRef.current?.checked || false;
          
          // Create preferences data
          preferencesData.optimization_level = optimizationLevel;
          preferencesData.theme_preferences = {
            use_dark_mode: user?.preferences?.theme_preferences?.use_dark_mode || false
          };
          preferencesData.notification_preferences = {
            email_alerts: emailAlerts,
            system_alerts: systemAlerts
          };
        }
        
        // Combine all data
        const userData = {
          profile: profileData,
          preferences: preferencesData
        };
        
        console.log("Updating profile with data:", userData);
        await dispatch(updateProfile(userData)).unwrap();
        setIsEditing(false);
        console.log("🧐 Sir Hawkington: 'Your profile has been updated with distinguished elegance!'");
      } catch (err: any) {
        console.error("Error updating profile:", err);
        setLocalError(err.message || "Failed to update profile");
        console.log("🧐 Sir Hawkington: 'Oh dear, it seems we've encountered a problem with your profile update.'");
      }
    } else {
      setIsEditing(true);
      console.log("🧐 Sir Hawkington: 'I see you wish to modify your digital persona. How splendid!'");
    }
  };
  
  // Loading state
  if (isLoading) {
    return (
      <div className="user-profile-modal visible">
        <div className="user-profile-card">
          <div className="loading-spinner">Loading profile...</div>
        </div>
      </div>
    );
  }
  
  // Not authenticated state
  if (!isAuthenticated) {
    return (
      <div className="user-profile-modal visible">
        <div className="user-profile-card">
          {onClose && (
            <button className="close-button" onClick={onClose}>
              ×
            </button>
          )}
          <h2 className="profile-title">Please log in</h2>
          {localError && (
            <div className="error-message">
              <p>{localError}</p>
              <button onClick={() => setLocalError(null)}>Dismiss</button>
            </div>
          )}
        </div>
      </div>
    );
  }
  
  // Main render
  return (
    <div className={`user-profile-modal ${isOpen ? 'visible' : ''}`}>
      <div className="user-profile-card">
        {onClose && (
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        )}
        <h2 className="profile-title">User Profile</h2>
        
        {localError && (
          <div className="error-message">
            <p>{localError}</p>
            <button onClick={() => setLocalError(null)}>Dismiss</button>
          </div>
        )}
        
        <div className="profile-header">
          <div className="profile-avatar">
            {getCharacterById(user?.profile?.avatar || 'sir-hawkington')}
          </div>
          <div className="profile-info">
            <h3 className="profile-username">{user?.username || 'Anonymous User'}</h3>
            <div className="profile-joined">
              Joined: {user?.profile?.joined_date ? new Date(user?.profile?.joined_date).toLocaleDateString() : 'Unknown'}
            </div>
            <div className="profile-email">{user?.email || ''}</div>
          </div>
        </div>
        
        <div className="profile-tabs">
          <button 
            className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
          <button 
            className={`tab-button ${activeTab === 'system' ? 'active' : ''}`}
            onClick={() => setActiveTab('system')}
          >
            System Info
          </button>
          <button 
            className={`tab-button ${activeTab === 'preferences' ? 'active' : ''}`}
            onClick={() => setActiveTab('preferences')}
          >
            Preferences
          </button>
        </div>
        
        <div className="tab-content">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="profile-tab-content">
              <div className="profile-section">
                <h3>Personal Information</h3>
                
                <div className="info-item">
                  <label>Username:</label>
                  <span>{user?.username}</span>
                </div>
                
                <div className="info-item">
                  <label>Email:</label>
                  {isEditing ? (
                    <input 
                      type="email" 
                      defaultValue={user?.email || ''} 
                      className="edit-input"
                      ref={emailRef}
                    />
                  ) : (
                    <span>{user?.email || 'Not provided'}</span>
                  )}
                </div>
                
                <div className="info-item bio-item">
                  <label>Bio:</label>
                  {isEditing ? (
                    <>
                      <textarea 
                        defaultValue={user?.profile?.bio || ''} 
                        className="edit-input bio-input"
                        ref={bioRef}
                        maxLength={300}
                        placeholder="Tell us about yourself (max 300 characters)"
                      />
                      <div className="bio-counter">
                        {bioRef.current?.value?.length || 0}/300
                      </div>
                    </>
                  ) : (
                    <span className="bio-text">{user?.profile?.bio || 'No bio provided'}</span>
                  )}
                </div>
              </div>
              
              <div className="avatar-section">
                <h3>Character Avatar</h3>
                <div className="current-avatar">
                  <label>Current Avatar:</label>
                  <div className="avatar-display">
                    {getCharacterById(user?.profile?.avatar || 'sir-hawkington')}
                    <span className="avatar-name">
                      {user?.profile?.avatar ? user?.profile?.avatar.split('-').map((word: string) => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') : 'Sir Hawkington'}
                    </span>
                  </div>
                </div>
                
                {isEditing && (
                  <CharacterAvatarSelector 
                    selectedAvatar={selectedAvatar} 
                    onSelect={handleAvatarSelect} 
                  />
                )}
              </div>
            </div>
          )}
          
          {/* System Info Tab */}
          {activeTab === 'system' && (
            <div className="system-tab-content">
              <div className="system-info-section">
                <h3>System Information</h3>
                <div className="info-item">
                  <label>Operating System:</label>
                  {isEditing ? (
                    <input 
                      type="text" 
                      defaultValue={`${user?.profile?.operating_system || ''} ${user?.profile?.os_version || ''}`} 
                      className="edit-input"
                      ref={osRef}
                    />
                  ) : (
                    <span>{user?.profile?.operating_system} {user?.profile?.os_version}</span>
                  )}
                </div>
                {user?.profile?.linux_distro && (
                  <div className="info-item">
                    <label>Distribution:</label>
                    {isEditing ? (
                      <input 
                        type="text" 
                        defaultValue={`${user?.profile?.linux_distro || ''} ${user?.profile?.linux_distro_version || ''}`} 
                        className="edit-input"
                        ref={distroRef}
                      />
                    ) : (
                      <span>{user?.profile?.linux_distro} {user?.profile?.linux_distro_version}</span>
                    )}
                  </div>
                )}
                <div className="info-item">
                  <label>CPU Cores:</label>
                  {isEditing ? (
                    <input 
                      type="number" 
                      defaultValue={user?.profile?.cpu_cores || 0} 
                      className="edit-input"
                      ref={cpuCoresRef}
                    />
                  ) : (
                    <span>{user?.profile?.cpu_cores}</span>
                  )}
                </div>
                <div className="info-item">
                  <label>Total Memory:</label>
                  {isEditing ? (
                    <input 
                      type="number" 
                      defaultValue={(user?.profile?.total_memory || 0) / 1024} 
                      className="edit-input"
                      step="0.1"
                      ref={memoryRef}
                    />
                  ) : (
                    <span>{(user?.profile?.total_memory || 0) / 1024} GB</span>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Preferences Tab */}
          {activeTab === 'preferences' && (
            <div className="preferences-tab-content">
              <div className="preferences-section">
                <h3>Optimization Preferences</h3>
                <div className="info-item">
                  <label>Optimization Level:</label>
                  {isEditing ? (
                    <select 
                      defaultValue={user?.preferences?.optimization_level || 'moderate'} 
                      className="edit-input"
                      ref={optimizationLevelRef}
                    >
                      <option value="conservative">Conservative</option>
                      <option value="moderate">Moderate</option>
                      <option value="aggressive">Aggressive</option>
                      <option value="meth_snail_overdrive">Meth Snail Overdrive</option>
                    </select>
                  ) : (
                    <span>{user?.preferences?.optimization_level}</span>
                  )}
                </div>
                
                <h3>Notification Preferences</h3>
                <div className="info-item checkbox-item">
                  <label>Email Alerts:</label>
                  {isEditing ? (
                    <input 
                      type="checkbox" 
                      defaultChecked={user?.preferences?.notification_preferences?.email_alerts || false} 
                      className="checkbox-input"
                      ref={emailAlertsRef}
                    />
                  ) : (
                    <span>{user?.preferences?.notification_preferences?.email_alerts ? 'Enabled' : 'Disabled'}</span>
                  )}
                </div>
                <div className="info-item checkbox-item">
                  <label>System Alerts:</label>
                  {isEditing ? (
                    <input 
                      type="checkbox" 
                      defaultChecked={user?.preferences?.notification_preferences?.system_alerts || false} 
                      className="checkbox-input"
                      ref={systemAlertsRef}
                    />
                  ) : (
                    <span>{user?.preferences?.notification_preferences?.system_alerts ? 'Enabled' : 'Disabled'}</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="profile-actions">
          <button 
            className={`edit-button ${isEditing ? 'save-mode' : ''}`}
            onClick={handleEditClick}
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : isEditing ? 'Save Changes' : 'Edit Profile'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
