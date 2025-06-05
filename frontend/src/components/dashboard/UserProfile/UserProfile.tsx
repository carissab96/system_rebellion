import React, { useRef } from 'react';
import { useAppSelector, useAppDispatch } from "../../../store/hooks";
import { updateProfile } from "../../../store/slices/authSlice";
import { UserProfile as ExtendedProfile, AuthState } from '../../../types/auth';

interface UserProfileProps {
  isOpen?: boolean;
  onClose?: () => void;
  isEditing?: boolean;
  onToggleEdit?: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ 
  isOpen, 
  onClose, 
  isEditing = false, 
  onToggleEdit 
}) => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading } = useAppSelector((state: { auth: AuthState }) => state.auth);

  // Fixed ref types - bio needs to be HTMLTextAreaElement since you're using textarea
  const bioRef = useRef<HTMLTextAreaElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);
  const systemAlertsRef = useRef<HTMLInputElement>(null);

  const handleAvatarSelect = (avatarId: string) => {
    if (isEditing) {
      dispatch(updateProfile({ avatar: avatarId }));
    }
  };

  const handleProfileUpdate = async () => {
    if (!isEditing) return;

    const bio = bioRef.current?.value || '';
    const email = emailRef.current?.value || '';
    const systemAlerts = systemAlertsRef.current?.checked || false;

    await dispatch(updateProfile({
      bio,
      email,
      preferences: {
        notification_preferences: {
          system_alerts: systemAlerts // Fixed property name consistency
        }
      }
    }));

    onToggleEdit?.();
  };

  const handleEditClick = () => {
    if (isEditing) {
      handleProfileUpdate();
    } else {
      onToggleEdit?.();
    }
  };

  if (!isAuthenticated) return null;

  return (
    <div className="profile-modal" style={{ display: isOpen ? 'block' : 'none' }}>
      <div className="profile-content">
        <div className="profile-header">
          <h2>System Guardian Profile</h2>
          <span className={`character-icon ${user?.avatar}`} />
        </div>
        
        <div className="profile-tabs">
          <div className="tab-content">
            <div className="profile-section">
              <h3>Profile Information</h3>
              
              <div className="info-item">
                <label>Username:</label>
                <span>{user?.username}</span>
              </div>
              
              <div className="info-item">
                <label>Bio:</label>
                {isEditing ? (
                  <textarea
                    ref={bioRef}
                    defaultValue={user?.profile?.bio || ''}
                    maxLength={300}
                  />
                ) : (
                  <span>{user?.profile?.bio || 'No bio set'}</span>
                )}
              </div>
              
              <div className="info-item">
                <label>Email:</label>
                {isEditing ? (
                  <input
                    type="email"
                    ref={emailRef}
                    defaultValue={user?.profile?.email || ''}
                  />
                ) : (
                  <span>{user?.profile?.email || 'No email set'}</span>
                )}
              </div>
              
              <div className="info-item checkbox-item">
                <label>System Alerts:</label>
                {isEditing ? (
                  <input 
                    type="checkbox" 
                    ref={systemAlertsRef}
                    defaultChecked={user?.preferences?.notification_preferences?.system_alerts || false} 
                    className="checkbox-input"
                  />
                ) : (
                  <span>
                    {user?.preferences?.notification_preferences?.system_alerts ? 'Enabled' : 'Disabled'}
                  </span>
                )}
              </div>
            </div>
          </div>
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