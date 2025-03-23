import * as React from 'react';
import { MemoryRouter } from 'react-router-dom';

type MockRouterProps = {
  children: React.ReactNode;
};

export const MockRouter: React.FC<MockRouterProps> = ({ children }) => (
  <MemoryRouter initialEntries={['/']}>{children}</MemoryRouter>
);