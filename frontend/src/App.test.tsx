import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders EvolveUI application', () => {
  render(<App />);
  // Look for something that should exist in the app, not a generic "learn react" link
  const element = screen.getByRole('button', { name: /show thinking process demo/i });
  expect(element).toBeInTheDocument();
});
