import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { GlassCard } from '../components/GlassCard';
import { motion } from 'framer-motion';
import { fetchChildren, fetchActivityLogs } from '../api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';

const Dashboard = () => {
  const { logout, token } = useAuth();
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [activityLogs, setActivityLogs] = useState([]);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const loadChildren = async () => {
      try {
        const data = await fetchChildren(token);
        setChildren(data);
        if (data.length > 0) {
          setSelectedChild(data[0]);
        }
      } catch (error) {
        console.error('Failed to load children', error);
      }
    };
    loadChildren();
  }, [token]);

  useEffect(() => {
    const loadLogs = async () => {
      if (selectedChild) {
        try {
          const logs = await fetchActivityLogs(selectedChild.id, token);
          setActivityLogs(logs);
          
          // Format for Recharts
          const formatted = logs.map(log => ({
            day: new Date(log.date).toLocaleDateString('en-US', { weekday: 'short' }),
            stress: log.stress_score || 0,
            screen: log.screen_time || 0
          })).reverse(); // Oldest to newest for line chart
          
          setChartData(formatted);
        } catch (error) {
          console.error('Failed to load logs', error);
        }
      }
    };
    loadLogs();
  }, [selectedChild, token]);

  return (
    <div className="container">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 className="stat-value">Dashboard</h1>
        <button className="btn-secondary" onClick={logout}>Sign Out</button>
      </header>

      <div className="grid-dashboard">
        {/* Child Selection Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <GlassCard>
            <h2 className="mb-2">Your Children</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {children.length === 0 ? (
                <p className="text-secondary">No children added yet.</p>
              ) : (
                children.map(child => (
                  <button
                    key={child.id}
                    className={selectedChild?.id === child.id ? 'btn-primary' : 'btn-secondary'}
                    onClick={() => setSelectedChild(child)}
                    style={{ textAlign: 'left' }}
                  >
                    {child.name} (Age {child.age})
                  </button>
                ))
              )}
              <button className="btn-secondary mt-1" style={{ borderStyle: 'dashed' }}>
                + Add Child
              </button>
            </div>
          </GlassCard>

          {/* AI Insights Snippet */}
          {selectedChild && activityLogs.length > 0 && (
            <GlassCard>
              <h3 className="mb-2" style={{ color: 'var(--accent-light)' }}>AI Insight: {selectedChild.name}</h3>
              <p className="text-secondary" style={{ fontSize: '0.9rem', lineHeight: '1.5' }}>
                <strong> Latest Prediction:</strong> {activityLogs[0].predicted_stress_level.toUpperCase()} Stress.
                <br/><br/>
                <em>(Advanced SHAP explanations will be rendered here based on real API data)</em>
              </p>
            </GlassCard>
          )}
        </div>

        {/* Main Analytics Area */}
        {selectedChild ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', gridColumn: 'span 2' }}>
            
            <GlassCard>
              <h3 className="mb-4">Weekly Stress Level vs Screen Time</h3>
              <div style={{ height: '300px', width: '100%' }}>
                {chartData.length > 0 ? (
                  <ResponsiveContainer>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="day" stroke="#94a3b8" />
                      <YAxis yAxisId="left" stroke="#ef4444" domain={[0, 100]} />
                      <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid #334155', borderRadius: '8px' }}
                      />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="stress" stroke="#ef4444" strokeWidth={3} activeDot={{ r: 8 }} />
                      <Line yAxisId="right" type="monotone" dataKey="screen" name="Screen Time (hrs)" stroke="#3b82f6" strokeWidth={3} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex-center" style={{ height: '100%' }}>
                    <p className="text-secondary">No activity logs yet. Please add a log.</p>
                  </div>
                )}
              </div>
            </GlassCard>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
              <GlassCard>
                <h3 className="mb-2">Average Sleep</h3>
                <p className="stat-value" style={{ color: 'var(--success)' }}>
                  {activityLogs.length > 0 
                    ? (activityLogs.reduce((acc, curr) => acc + curr.sleep_duration, 0) / activityLogs.length).toFixed(1) 
                    : 0} hrs
                </p>
              </GlassCard>
              <GlassCard>
                <h3 className="mb-2">Current Status</h3>
                <p className="stat-value" style={{ color: activityLogs.length > 0 && activityLogs[0].predicted_stress_level === 'low' ? 'var(--success)' : 'var(--warning)' }}>
                  {activityLogs.length > 0 ? activityLogs[0].predicted_stress_level.toUpperCase() : 'N/A'}
                </p>
              </GlassCard>
            </div>

          </div>
        ) : (
          <div style={{ gridColumn: 'span 2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p className="text-secondary">Please select or add a child to view analytics.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
