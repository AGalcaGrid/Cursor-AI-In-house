import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import type { 
  User, 
  AuthTokens, 
  AuthState, 
  AuthContextType, 
  LoginCredentials, 
  RegisterData 
} from '../types/auth';

const TOKEN_STORAGE_KEY = 'auth_tokens';
const USER_STORAGE_KEY = 'auth_user';
const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes before expiry

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const getStoredTokens = (): AuthTokens | null => {
  try {
    const stored = localStorage.getItem(TOKEN_STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
};

const getStoredUser = (): User | null => {
  try {
    const stored = localStorage.getItem(USER_STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
};

const storeTokens = (tokens: AuthTokens): void => {
  localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
};

const storeUser = (user: User): void => {
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
};

const clearStorage = (): void => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
};

const isTokenExpired = (tokens: AuthTokens): boolean => {
  return Date.now() >= tokens.expiresAt;
};

const shouldRefreshToken = (tokens: AuthTokens): boolean => {
  return Date.now() >= tokens.expiresAt - TOKEN_REFRESH_THRESHOLD;
};

interface AuthProviderProps {
  children: ReactNode;
  apiBaseUrl?: string;
}

export function AuthProvider({ children, apiBaseUrl = '/api' }: AuthProviderProps) {
  const [state, setState] = useState<AuthState>({
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error, isLoading: false }));
  };

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const apiRequest = async <T,>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const response = await fetch(`${apiBaseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Request failed: ${response.status}`);
    }

    return response.json();
  };

  const authenticatedRequest = async <T,>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    const tokens = getStoredTokens();
    if (!tokens) {
      throw new Error('No authentication tokens');
    }

    if (shouldRefreshToken(tokens)) {
      const refreshed = await refreshAccessToken();
      if (!refreshed) {
        throw new Error('Token refresh failed');
      }
    }

    const currentTokens = getStoredTokens();
    return apiRequest<T>(endpoint, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${currentTokens?.accessToken}`,
      },
    });
  };

  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    const tokens = getStoredTokens();
    if (!tokens?.refreshToken) {
      return false;
    }

    try {
      const response = await apiRequest<{ access_token: string; expires_in: number }>(
        '/auth/refresh',
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${tokens.refreshToken}`,
          },
        }
      );

      const newTokens: AuthTokens = {
        ...tokens,
        accessToken: response.access_token,
        expiresAt: Date.now() + response.expires_in * 1000,
      };

      storeTokens(newTokens);
      setState(prev => ({ ...prev, tokens: newTokens }));
      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
      return false;
    }
  }, [apiBaseUrl]);

  const login = useCallback(async (credentials: LoginCredentials): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await apiRequest<{
        user: User;
        access_token: string;
        refresh_token: string;
        expires_in: number;
      }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      });

      const tokens: AuthTokens = {
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        expiresAt: Date.now() + response.expires_in * 1000,
      };

      storeTokens(tokens);
      storeUser(response.user);

      setState({
        user: response.user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Login failed');
      throw error;
    }
  }, [apiBaseUrl]);

  const register = useCallback(async (data: RegisterData): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await apiRequest<{
        user: User;
        access_token: string;
        refresh_token: string;
        expires_in: number;
      }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      const tokens: AuthTokens = {
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        expiresAt: Date.now() + response.expires_in * 1000,
      };

      storeTokens(tokens);
      storeUser(response.user);

      setState({
        user: response.user,
        tokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Registration failed');
      throw error;
    }
  }, [apiBaseUrl]);

  const logout = useCallback((): void => {
    clearStorage();
    setState({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  }, []);

  useEffect(() => {
    const initializeAuth = async () => {
      const storedTokens = getStoredTokens();
      const storedUser = getStoredUser();

      if (!storedTokens || !storedUser) {
        setState(prev => ({ ...prev, isLoading: false }));
        return;
      }

      if (isTokenExpired(storedTokens)) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          clearStorage();
          setState(prev => ({ ...prev, isLoading: false }));
          return;
        }
      }

      setState({
        user: storedUser,
        tokens: storedTokens,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    };

    initializeAuth();
  }, [refreshAccessToken]);

  useEffect(() => {
    if (!state.tokens || !state.isAuthenticated) return;

    const timeUntilRefresh = state.tokens.expiresAt - Date.now() - TOKEN_REFRESH_THRESHOLD;
    if (timeUntilRefresh <= 0) return;

    const refreshTimer = setTimeout(() => {
      refreshAccessToken();
    }, timeUntilRefresh);

    return () => clearTimeout(refreshTimer);
  }, [state.tokens, state.isAuthenticated, refreshAccessToken]);

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshAccessToken,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export { authenticatedRequest };

export function useAuthenticatedFetch() {
  const { tokens, refreshAccessToken, logout } = useAuth();

  const fetchWithAuth = useCallback(
    async <T,>(url: string, options: RequestInit = {}): Promise<T> => {
      if (!tokens) {
        throw new Error('Not authenticated');
      }

      if (shouldRefreshToken(tokens)) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          logout();
          throw new Error('Session expired');
        }
      }

      const currentTokens = getStoredTokens();
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${currentTokens?.accessToken}`,
          ...options.headers,
        },
      });

      if (response.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          const retryTokens = getStoredTokens();
          const retryResponse = await fetch(url, {
            ...options,
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${retryTokens?.accessToken}`,
              ...options.headers,
            },
          });
          if (!retryResponse.ok) {
            throw new Error(`Request failed: ${retryResponse.status}`);
          }
          return retryResponse.json();
        } else {
          logout();
          throw new Error('Session expired');
        }
      }

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      return response.json();
    },
    [tokens, refreshAccessToken, logout]
  );

  return fetchWithAuth;
}
