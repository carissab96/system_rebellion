// src/store/slices/index.ts
import authReducer, { 
  login, 
  register, 
  logout, 
  checkAuthStatus, 
  updateProfile,
  clearError
} from './authSlice';

import userProfileReducer, {
  fetchUserProfile,
  clearProfileError
} from './userProfileSlice';

// Export reducers
export {
  authReducer,
  userProfileReducer
};

// Export actions
export {
  // Auth actions
  login,
  register,
  logout,
  checkAuthStatus,
  updateProfile,
  clearError,
  
  // User profile actions
  fetchUserProfile,
  clearProfileError
};
