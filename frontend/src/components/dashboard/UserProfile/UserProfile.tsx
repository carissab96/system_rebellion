import React, { useState, useRef } from "react";
import { useAppSelector, useAppDispatch } from "../../../store/hooks";
import { updateProfile } from "../../../store/slices/authSlice";
import { CharacterAvatarSelector, getCharacterById } from "../../common/CharacterIcons";
import "./UserProfile.css";

export const UserProfile: React.FC = () => {
    const dispatch = useAppDispatch();
    const user = useAppSelector(state => state.auth.user);
    const profile = useAppSelector(state => state.auth.user?.profile);
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
    
    const handleEditClick = () => {
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
        
        // Dispatch action to update profile
        dispatch(updateProfile({
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
        }));
        
        console.log("✨ Sir Hawkington has saved your profile changes with aristocratic flair!");
      } else {
        console.log("📝 Sir Hawkington is now in edit mode, adjusting his monocle for precision...");
      }
      
      setIsEditing(!isEditing);
    };
  
    return (
      <div className="user-profile-card">
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
                {profile?.avatar ? profile.avatar.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') : 'Sir Hawkington'}
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
  