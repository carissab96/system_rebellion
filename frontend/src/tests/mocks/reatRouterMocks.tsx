import React from 'react';
import { MemoryRouter } from 'react-router-dom';

export const MockRouter: React.FC = ({ children }) => (
  <MemoryRouter initialEntries={['/']}>{children}</MemoryRouter>
);