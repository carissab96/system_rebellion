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
  };
  preferences: {
    optimization_level: string;
    theme_preferences: {
      use_dark_mode: boolean;
    };
  };
}

interface UserProfileProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ isOpen, onClose }) => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading, error } = useAppSelector(state => state.auth as { user: ExtendedProfile & { username: string }, isAuthenticated: boolean, isLoading: boolean, error: string | null });
  const [localError, setLocalError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedAvatar, setSelectedAvatar] = useState<string>('sir-hawkington');
  
  // Refs to store the edited values
  const osRef = useRef<HTMLInputElement>(null);
  const distroRef = useRef<HTMLInputElement>(null);
  const cpuCoresRef = useRef<HTMLInputElement>(null);
  const memoryRef = useRef<HTMLInputElement>(null);
  const optimizationLevelRef = useRef<HTMLSelectElement>(null);
  
  // Fetch user data when component mounts
  useEffect(() => {
    if (!user && isAuthenticated) {
      dispatch(checkAuthStatus());
    }
  }, [user, isAuthenticated, dispatch]);
  
  // Set the selected avatar when user data loads
  useEffect(() => {
    console.log("User data changed:", user);
    if (user?.profile?.avatar) {
      console.log("Setting selected avatar to", user.profile.avatar);
      setSelectedAvatar(user.profile.avatar);
    } else {
      console.log("No avatar found in user profile");
    }
  }, [user]);
    
    //Update error state when Redux error changes
    useEffect(() => {
      if (error) {
        console.log("Updating local error to", error);
        setLocalError(error);
      }
    }, [error]);
    
// Handle avatar selection
const handleAvatarSelect = (avatarId: string) => {
      console.log("Setting selected avatar to", avatarId);
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
      // Get values from refs
      const osValue = osRef.current?.value || '';
      const distroValue = distroRef.current?.value || '';
      const cpuCores = Number(cpuCoresRef.current?.value || 0);
      const memory = Number(memoryRef.current?.value || 0) * 1024; // Convert GB to MB
      const optimizationLevel = optimizationLevelRef.current?.value || 'moderate';
      
      // Split OS and distro
      const osParts = osValue.split(' ');
      const osName = osParts[0] || '';
      const osVersion = osParts.slice(1).join(' ') || '';
      
      const distroParts = distroValue.split(' ');
      const distroName = distroParts[0] || '';
        const distroVersion = distroParts.slice(1).join(' ') || '';
      
      // Create profile data in the format expected by the backend
      // The backend expects either direct properties or a nested system_info object
      const profileData = {
        operating_system: osName,
        os_version: osVersion,
        linux_distro: distroName,
        linux_distro_version: distroVersion,
        cpu_cores: cpuCores,
        total_memory: memory,
        avatar: selectedAvatar,
        preferences: {
          optimization_level: optimizationLevel,
          theme_preferences: {
            use_dark_mode: true
          }
        }
      };
      
      console.log(`🧐 Sir Hawkington: "Submitting your profile changes with utmost elegance!"`);
      console.log('Profile data being sent:', profileData);
      
      // Dispatch update profile action
      await dispatch(updateProfile(profileData)).unwrap();
      
      // Exit edit mode
      setIsEditing(false);
      console.log(`🧐 Sir Hawkington: "Your profile has been updated with distinguished precision!"`);
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      setLocalError(error.message || 'Failed to update profile');
    }
  } else {
    // Enter edit mode
    setIsEditing(true);
    console.log(`🧐 Sir Hawkington: "I see you wish to modify your digital persona. How splendid!"`);
  }
};

// Handle escape key
useEffect(() => {
  const handleEscapeKey = (event: KeyboardEvent) => {
    if (event.key === 'Escape' && onClose) {
          console.log("Closing user profile modal...");
      onClose();
    }
  };
  
  if (isOpen) {
    document.addEventListener('keydown', handleEscapeKey);
  }

  return () => {
    document.removeEventListener('keydown', handleEscapeKey);
  };
}, [isOpen, onClose]);

// Don't render if not open
if (isOpen === false) {
  return null;
}

// Loading state
if (isLoading) {
  return (
    <div className={`user-profile-card ${isOpen ? 'visible' : ''}`}>
      <h2 className="profile-title">Loading profile...</h2>
    </div>
  );
}

// No user state
if (!user) {
  return (
    <div className={`user-profile-card ${isOpen ? 'visible' : ''}`}>
      <h2 className="profile-title">Please log in</h2>
      {localError && (
        <div className="error-message">
          <p>{localError}</p>
          <button onClick={() => setLocalError(null)}>Dismiss</button>
        </div>
      )}
    </div>
  );
}

// Main render
return (
  <div className={`user-profile-card ${isOpen ? 'visible' : ''}`}>
    {onClose && (
      <button className="close-button" onClick={onClose}>
        ×
      </button>
    )}
    <h2 className="profile-title">System Profile</h2>
    
    {localError && (
    <div className="error-message">
      <p>{localError}</p>
      <button onClick={() => setLocalError(null)}>Dismiss</button>
    </div>
  )}
  
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
  
  <button 
    className={`edit-button ${isEditing ? 'save-mode' : ''}`}
    onClick={handleEditClick}
    disabled={isLoading}
  >
    {isLoading ? 'Processing...' : isEditing ? 'Save Changes' : 'Edit'}
  </button>
  </div>
  );
};