import { useAuth } from './contexts/AuthContext';

export function TestAuth() {
  const { isAuthenticated, user } = useAuth();
  
  return (
    <div style={{ padding: '20px', background: 'white', color: 'black' }}>
      <h1>Auth Test</h1>
      <p>Authenticated: {isAuthenticated ? 'Yes' : 'No'}</p>
      <p>User: {user?.username || 'None'}</p>
    </div>
  );
}
