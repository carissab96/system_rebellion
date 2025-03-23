// src/tests/AuthComponent.test.tsx
import { render, fireEvent, waitFor } from '@testing-library/react'
import { Login } from '../components/Auth/login/Login'
import { login } from '../store/slices/authSlice'

describe('Authentication Component', () => {
  it('handles successful login', async () => {
    const { getByTestId } = render(<Login />)
    
    fireEvent.change(getByTestId('username'), { 
      target: { value: 'testuser' } 
    })
    fireEvent.change(getByTestId('password'), { 
      target: { value: 'SecureP@ssw0rd123!' } 
    })
    
    fireEvent.click(getByTestId('login-button'))
    
    await waitFor(() => {
      expect(login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'SecureP@ssw0rd123!'
      })
    })
  })
})