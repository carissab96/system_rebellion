export const mockApiCalls = () => {
    jest.mock('../utils/api', () => ({
      initializeCsrf: jest.fn(() => Promise.resolve(true)),
      checkBackendAvailability: jest.fn(() => Promise.resolve(true))
    }));
  };