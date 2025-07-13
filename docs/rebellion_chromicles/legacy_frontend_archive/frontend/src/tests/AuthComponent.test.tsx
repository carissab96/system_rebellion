// src/tests/AuthComponent.test.tsx
import { render, fireEvent, waitFor } from '@testing-library/react'
import Login from '../components/Auth/login/Login'
import { login } from '../store/slices/authSlice'

describe('Authentication Component', () => {
  it('handles successful login', async () => {
    const { getByTestId } = render(<Login onClose={function (): void {
      throw new Error('Function not implemented.')
    } } isOpen={true} />)
    
    fireEvent.change(getByTestId('username'), { 
      target: { value: 'testuser' } 
    })
    fireEvent.change(getByTestId('password'), { 
      target: { value: 'testpassword' } 
    })
    
    fireEvent.click(getByTestId('login-button'))
    
    await waitFor(() => {
      expect(login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'testpassword'
      })
    })
  })
})