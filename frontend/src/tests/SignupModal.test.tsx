
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../store/slices/authSlice';
import SignupModal from '../components/Auth/SignupModal/SignupModal';

const mockStore = configureStore({
  reducer: {
    auth: authReducer
  }
});

const mockOnClose = jest.fn();

const renderComponent = (isOpen = true) => {
  return render(
    <Provider store={mockStore}>
      <BrowserRouter>
        <SignupModal isOpen={isOpen} onClose={mockOnClose} />
      </BrowserRouter>
    </Provider>
  );
};

describe('SignupModal Component', () => {
  it('renders signup form', () => {
    renderComponent();
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
  });

  it('allows entering user details', () => {
    renderComponent();
    
    const usernameInput = screen.getByLabelText(/username/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    
    fireEvent.change(usernameInput, { target: { value: 'newuser' } });
    fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123!' } });
    
    expect(usernameInput).toHaveValue('newuser');
    expect(emailInput).toHaveValue('newuser@example.com');
    expect(passwordInput).toHaveValue('Password123!');
    expect(confirmPasswordInput).toHaveValue('Password123!');
  });

  it('submits form with user details', async () => {
    const mockRegister = jest.fn(() => Promise.resolve({
      user: { 
        id: '1', 
        username: 'newuser',
        email: 'newuser@example.com'
      }
    }));

    // Mock the registerUser action in the store
    jest.spyOn(mockStore.dispatch, 'dispatch').mockImplementation(mockRegister);

    renderComponent();
    
    // Fill out the form
    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'newuser' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'newuser@example.com' } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'Password123!' } });
    
    // Select OS and other required fields
    fireEvent.change(screen.getByLabelText(/operating system/i), { target: { value: 'Linux' } });
    fireEvent.change(screen.getByLabelText(/os version/i), { target: { value: '22.04' } });
    fireEvent.change(screen.getByLabelText(/cpu cores/i), { target: { value: '4' } });
    fireEvent.change(screen.getByLabelText(/total memory/i), { target: { value: '8' } });
    
    const submitButton = screen.getByRole('button', { name: /join the system rebellion/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith(
        expect.objectContaining({
          username: 'newuser',
          email: 'newuser@example.com',
          password: 'Password123!',
          profile: expect.any(Object)
        })
      );
    });
  });
});