import { Request, Response, NextFunction } from 'express';
import { AuthUtils } from '../utils/helpers';
import { UserRole, JwtPayload } from '../types';
import logger from '../utils/logger';

export interface AuthenticatedRequest extends Request {
  user?: JwtPayload;
}

export const authenticate = (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      res.status(401).json({
        success: false,
        error: 'Access token required',
        timestamp: new Date(),
        path: req.path,
        method: req.method,
      });
      return;
    }

    const token = authHeader.substring(7);
    const payload = AuthUtils.verifyToken(token);
    
    req.user = payload;
    next();
  } catch (error) {
    logger.error('Authentication error:', error);
    res.status(401).json({
      success: false,
      error: 'Invalid or expired token',
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  }
};

export const authorize = (roles: UserRole[]) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        success: false,
        error: 'Authentication required',
        timestamp: new Date(),
        path: req.path,
        method: req.method,
      });
      return;
    }

    if (!AuthUtils.hasRole(req.user.role, roles)) {
      res.status(403).json({
        success: false,
        error: 'Insufficient permissions',
        timestamp: new Date(),
        path: req.path,
        method: req.method,
      });
      return;
    }

    next();
  };
};

export const optionalAuth = (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
  try {
    const authHeader = req.headers.authorization;
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      const payload = AuthUtils.verifyToken(token);
      req.user = payload;
    }
    
    next();
  } catch (error) {
    // For optional auth, we don't fail on invalid tokens
    logger.warn('Optional auth failed:', error);
    next();
  }
};