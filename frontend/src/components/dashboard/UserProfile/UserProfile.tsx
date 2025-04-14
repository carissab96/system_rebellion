import React, { useState, useRef, useEffect } from "react";
import { useAppSelector, useAppDispatch } from "../../../store/hooks";
import { updateProfile } from "../../../store/slices/authSlice";
import { CharacterAvatarSelector, getCharacterById } from "../../common/CharacterIcons";
import axios from "axios";
import "./UserProfile.css";

// Define extended profile interface to include all possible fields
interface ExtendedProfile {
  operating_system: string;
  os_version: string;
  cpu_cores: number;
  total_memory: number;
  linux_distro?: string;
  linux_distro_version?: string;
  avatar?: string;
  [key: string]: any; // Allow for additional fields
}

interface UserProfileProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ isOpen, onClose }) => {
    const dispatch = useAppDispatch();
    const user = useAppSelector(state => state.auth.user);
    
    // Debug user state to understand what's happening
    useEffect(() => {
      console.log('🧐 User state in UserProfile:', user);
      
      // If user is null but we have a username in localStorage, try to load the profile
      if (!user && localStorage.getItem('username')) {
        const loadProfileData = async () => {
          try {
            const username = localStorage.getItem('username');
            const token = localStorage.getItem('token');
            
            if (username && token) {
              console.log('🧐 Attempting to load profile data for:', username);
              
              const response = await axios.get(`/api/auth/auth-status`, {
                headers: {
                  'Authorization': `Bearer ${token}`
                },
                withCredentials: true
              });
              
              if (response.data && response.data.user) {
                console.log('✅ Loaded user data from server:', response.data.user);
                dispatch(updateProfile(response.data.user));
              }
            }
          } catch (error: any) {
            console.error('❌ Failed to load profile data:', error.message);
          }
        };
        
        loadProfileData();
      }
    }, [user, dispatch]);
    
    // Get profile data from either nested profile object or direct user fields
    const getProfileData = () => {
      if (!user) return null;
      
      // Create a merged profile object that combines both sources
      const mergedProfile: ExtendedProfile = {
        // Start with any existing profile data
        ...(user.profile as ExtendedProfile || {}),
        
        // Override with direct user fields if they exist
        operating_system: user.operating_system || (user.profile as ExtendedProfile | undefined)?.operating_system || '',
        os_version: user.os_version || (user.profile as ExtendedProfile | undefined)?.os_version || '',
        linux_distro: user.linux_distro || (user.profile as ExtendedProfile | undefined)?.linux_distro || '',
        linux_distro_version: user.linux_distro_version || (user.profile as ExtendedProfile | undefined)?.linux_distro_version || '',
        cpu_cores: user.cpu_cores || (user.profile as ExtendedProfile | undefined)?.cpu_cores || 0,
        total_memory: user.total_memory || (user.profile as ExtendedProfile | undefined)?.total_memory || 0,
        avatar: user.avatar || (user.profile as ExtendedProfile | undefined)?.avatar || 'sir-hawkington'
      };
      
      console.log('🧐 Sir Hawkington has merged the profile data:', mergedProfile);
      return mergedProfile;
    };
    
    const profile = getProfileData();
    const [isEditing, setIsEditing] = useState(false);
    const [selectedAvatar, setSelectedAvatar] = useState<string>(profile?.avatar || 'sir-hawkington');
    
    // Refs to store the edited values
    const osRef = useRef<HTMLInputElement>(null);
    const distroRef = useRef<HTMLInputElement>(null);
    const cpuCoresRef = useRef<HTMLInputElement>(null);
    const memoryRef = useRef<HTMLInputElement>(null);
    const optimizationLevelRef = useRef<HTMLSelectElement>(null);
    
    // Handle avatar selection
    const handleAvatarSelect = (avatarId: string) => {
        setSelectedAvatar(avatarId);
        console.log(`🧐 Sir Hawkington: "Ah, I see you've chosen ${avatarId} as your digital persona. Splendid choice!"`); 
    };
    
    const handleEditClick = async () => {
      console.log("🧐 Sir Hawkington is preparing his quill to edit your distinguished profile...");
      
      if (isEditing) {
        // Save changes
        const osValue = osRef.current?.value || '';
        const distroValue = distroRef.current?.value || '';
        const cpuCores = Number(cpuCoresRef.current?.value || 0);
        const memory = Number(memoryRef.current?.value || 0) * 1024; // Convert back to MB
        const optimizationLevel = optimizationLevelRef.current?.value || 'moderate';
        
        // Split OS into name and version (simple split on space)
        const osParts = osValue.split(' ');
        const osName = osParts[0] || '';
        const osVersion = osParts.slice(1).join(' ') || '';
        
        // Split distro into name and version (simple split on space)
        const distroParts = distroValue.split(' ');
        const distroName = distroParts[0] || '';
        const distroVersion = distroParts.slice(1).join(' ') || '';
        
        // Create profile data object
        const profileData = {
          profile: {
            operating_system: osName,
            os_version: osVersion,
            linux_distro: distroName,
            linux_distro_version: distroVersion,
            cpu_cores: cpuCores,
            total_memory: memory,
            avatar: selectedAvatar
          },
          preferences: {
            optimization_level: optimizationLevel,
            theme_preferences: {
              use_dark_mode: true // Default to dark mode for cyberpunk aesthetic
            }
          }
        };
        
        try {
          // Get username from localStorage - this is our source of truth
          const username = localStorage.getItem('username');
          const token = localStorage.getItem('token');
          
          if (!username) {
            console.error("❌ Cannot update profile: No username found in localStorage");
            throw new Error("Username not found in state. Please log in again.");
          }
          
          if (!token) {
            console.error("❌ Cannot update profile: No token found in localStorage");
            throw new Error("Authentication token not found. Please log in again.");
          }
          
          console.log("🧐 Sir Hawkington is sending your profile data to the server for user:", username);
          
          // First update local state via Redux
          dispatch(updateProfile({
            ...profileData,
            username: username // Ensure username is in the user object
          }));
          
          // Check if the user exists in the backend before updating
          try {
            // Verify user exists by checking status
            const statusCheck = await axios.get(`/api/auth/status/`, {
              headers: {
                'Authorization': `Bearer ${token}`
              },
              withCredentials: true
            });
            
            console.log("🧐 User status check:", statusCheck.data);
            
            if (!statusCheck.data.is_authenticated) {
              console.error("❌ User is not authenticated according to status check");
              throw new Error("Authentication failed. Please log in again.");
            }
          } catch (statusError) {
            console.error("❌ Error checking user status:", statusError);
            // Continue anyway - we'll let the profile update attempt handle errors
          }
          
          // Then send to the backend
          const response = await axios.post(
            `/api/auth/direct-profile-update/${username}`,
            profileData,
            {
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              withCredentials: true
            }
          );
          
          console.log("✅ Profile data saved to server:", response.data);
          
          // Update Redux store with the returned user data
          if (response.data && response.data.user) {
            // Make sure to include the username in the update
            dispatch(updateProfile({
              ...response.data.user,
              username: username
            }));
          }
          
          console.log("✨ Sir Hawkington has saved your profile changes with aristocratic flair!");
        } catch (error) {
          console.error("❌ Error updating user information:", error);
        }
      } else {
        console.log("📝 Sir Hawkington is now in edit mode, adjusting his monocle for precision...");
      }
      
      setIsEditing(!isEditing);
    };
  
    // Handle escape key press
    useEffect(() => {
      const handleEscapeKey = (event: KeyboardEvent) => {
        if (event.key === 'Escape' && onClose) {
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

    // Don't render anything if not open and isOpen prop is provided
    if (isOpen === false) {
      return null;
    }

    return (
      <div className={`user-profile-card ${isOpen ? 'visible' : ''}`}>
        {onClose && (
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        )}
        <h2 className="profile-title">System Profile</h2>
  
        <div className="system-info-section">
          <h3>System Information</h3>
          <div className="info-item">
            <label>Operating System:</label>
            {isEditing ? (
              <input 
                type="text" 
                defaultValue={`${profile?.operating_system || ''} ${profile?.os_version || ''}`} 
                className="edit-input"
                ref={osRef}
              />
            ) : (
              <span>{profile?.operating_system} {profile?.os_version}</span>
            )}
          </div>
          {profile?.linux_distro && (
            <div className="info-item">
              <label>Distribution:</label>
              {isEditing ? (
                <input 
                  type="text" 
                  defaultValue={`${profile?.linux_distro || ''} ${profile?.linux_distro_version || ''}`} 
                  className="edit-input"
                  ref={distroRef}
                />
              ) : (
                <span>{profile?.linux_distro} {profile?.linux_distro_version}</span>
              )}
            </div>
          )}
          <div className="info-item">
            <label>CPU Cores:</label>
            {isEditing ? (
              <input 
                type="number" 
                defaultValue={profile?.cpu_cores || 0} 
                className="edit-input"
                ref={cpuCoresRef}
              />
            ) : (
              <span>{profile?.cpu_cores}</span>
            )}
          </div>
          <div className="info-item">
            <label>Total Memory:</label>
            {isEditing ? (
              <input 
                type="number" 
                defaultValue={(profile?.total_memory || 0) / 1024} 
                className="edit-input"
                step="0.1"
                ref={memoryRef}
              />
            ) : (
              <span>{(profile?.total_memory || 0) / 1024} GB</span>
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
              {getCharacterById(profile?.avatar || 'sir-hawkington')}
              <span className="avatar-name">
                {profile?.avatar ? profile.avatar.split('-').map((word: string) => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') : 'Sir Hawkington'}
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
        >
          {isEditing ? 'Save Changes' : 'Edit'}
        </button>
      </div>
    );
  };
  