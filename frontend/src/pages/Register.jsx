import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/GlassCard';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { registerAPI, loginAPI } from '../api';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await registerAPI(name, email, password);
      const data = await loginAPI(email, password); // Auto login
      login(data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed.');
    }
  };

  return (
    <div className="container flex-center" style={{ minHeight: '100vh' }}>
      <GlassCard className="text-center" style={{ width: '100%', maxWidth: '400px' }}>
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, type: 'spring' }}
        >
          <h1 className="mb-2 stat-value" style={{ fontSize: '2.5rem' }}>MindMitra AI</h1>
          <p className="text-secondary mb-4">Create your parent account.</p>
        </motion.div>

        {error && <p style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</p>}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <input 
              type="text" 
              placeholder="Full Name" 
              className="input-field"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="mb-4">
            <input 
              type="email" 
              placeholder="Email address" 
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="mb-4">
            <input 
              type="password" 
              placeholder="Password" 
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn-primary" style={{ width: '100%' }}>
            Sign Up
          </button>
        </form>
        <p className="mt-4 text-secondary" style={{ fontSize: '0.9rem' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-light)' }}>Log in</Link>
        </p>
      </GlassCard>
    </div>
  );
};

export default Register;
