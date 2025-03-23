import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../store/slices/authSlice';
import { Login } from '../components/Auth/login/Login';

// Mock dependencies
jest.mock('../utils/api', () => ({
  initializeCsrf: jest.fn(() => Promise.resolve(true)),
  checkBackendAvailability: jest.fn(() => Promise.resolve(true))
}));

const mockStore = configureStore({
  reducer: {
    auth: authReducer
  }
});

const renderComponent = () => {
  return render(
    <Provider store={mockStore}>
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    </Provider>
  );
};

describe('Login Component', () => {
  it('renders login form', () => {
    renderComponent();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /enter the system rebellion/i })).toBeInTheDocument();
  });

  it('allows entering username and password', () => {
    renderComponent();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
   
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(usernameInput).toHaveValue('testuser');
    expect(passwordInput).toHaveValue('password123');
  });

  it('submits form with credentials', async () => {
    const mockLogin = jest.fn(() => Promise.resolve({
      data: { 
        access: 'fake-token',
        user: { id: '1', username: 'testuser' }
      }
    }));

    // Mock the dispatch method to return the action (which would be the first argument)
    jest.spyOn(mockStore, 'dispatch').mockImplementation((action) => {
      mockLogin();
      return action; // Return the action to satisfy TypeScript
    });

    renderComponent();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /enter the system rebellion/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith(
        expect.objectContaining({
          username: 'testuser',
          password: 'password123'
        })
      );
    });
  });

  it('opens signup modal', () => {
    renderComponent();
    
    const signupButton = screen.getByRole('button', { name: /join the system rebellion/i });
    fireEvent.click(signupButton);
    
    // This would typically check if the signup modal is rendered
    // You might need to mock the SignupModal component
  });
});