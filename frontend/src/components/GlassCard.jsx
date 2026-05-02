import { motion } from 'framer-motion';

export const GlassCard = ({ children, className = '', ...props }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className={`glass-card ${className}`} 
      {...props}
    >
      {children}
    </motion.div>
  );
};
