/**
 * Test setup file for authentication and form testing
 */

import '@testing-library/jest-dom';
// import { server } from './mocks/server';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  usePathname: () => '/test',
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: 'div',
    form: 'form',
    button: 'button',
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock window.location for URL parameter testing
Object.defineProperty(window, 'location', {
  value: {
    search: '',
    origin: 'http://localhost:3000',
    href: 'http://localhost:3000',
  },
  writable: true,
});

// Setup MSW (commented out for now due to import issues)
// beforeAll(() => server.listen());
// afterEach(() => server.resetHandlers());
// afterAll(() => server.close());