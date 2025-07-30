import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import LoadingSpinner from './LoadingSpinner';
import './animations.css';

interface RouteTransitionProps {
  children: React.ReactNode;
}

type AnimationDirection = 'left' | 'right' | 'up' | 'down' | 'fade';

const RouteTransition: React.FC<RouteTransitionProps> = ({ children }) => {
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(true);
  const [showContent, setShowContent] = useState(false);
  const [direction, setDirection] = useState<AnimationDirection>('fade');
  const [prevPathname, setPrevPathname] = useState('');
  
  // Determine animation direction based on navigation path
  useEffect(() => {
    if (prevPathname) {
      // Simple heuristic for direction:
      // If going from a deeper path to a shallower one, animate from right
      // Otherwise animate from left
      const prevDepth = prevPathname.split('/').length;
      const currentDepth = location.pathname.split('/').length;
      
      if (prevDepth > currentDepth) {
        setDirection('right');
      } else if (prevDepth < currentDepth) {
        setDirection('left');
      } else {
        // Same depth, use fade as default
        setDirection('fade');
      }
    }
    
    setPrevPathname(location.pathname);
  }, [location.pathname]);
  
  useEffect(() => {
    // Set loading to true when the route changes
    setIsLoading(true);
    setShowContent(false);
    
    // Use a small timeout to ensure CSS is applied before showing content
    const timer = setTimeout(() => {
      setIsLoading(false);
      
      // Small delay before showing content with animation
      setTimeout(() => {
        setShowContent(true);
      }, 50);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [location.pathname]);
  
  // Get animation class based on direction
  const getAnimationClass = () => {
    switch (direction) {
      case 'left':
        return 'slide-left';
      case 'right':
        return 'slide-right';
      case 'up':
      case 'down':
      case 'fade':
      default:
        return 'fade';
    }
  };
  
  return (
    <>
      {isLoading ? (
        <div className="min-h-[200px] flex items-center justify-center">
          <LoadingSpinner />
        </div>
      ) : (
        <div 
          className={`${showContent ? `${getAnimationClass()}-enter-active` : `${getAnimationClass()}-enter`}`}
          style={{
            animationDuration: '0.4s',
            animationFillMode: 'forwards'
          }}
        >
          {children}
        </div>
      )}
    </>
  );
};

export default RouteTransition;