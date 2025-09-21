import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { config } from '../config';
import { JwtPayload, UserRole } from '../types';

export class AuthUtils {
  static async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, config.security.bcryptRounds);
  }

  static async comparePassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  static generateAccessToken(payload: Omit<JwtPayload, 'iat' | 'exp'>): string {
    return jwt.sign(
      payload, 
      config.jwt.secret, 
      { expiresIn: config.jwt.expiresIn } as jwt.SignOptions
    );
  }

  static generateRefreshToken(payload: Omit<JwtPayload, 'iat' | 'exp'>): string {
    return jwt.sign(
      payload, 
      config.jwt.secret, 
      { expiresIn: config.jwt.refreshExpiresIn } as jwt.SignOptions
    );
  }

  static verifyToken(token: string): JwtPayload {
    return jwt.verify(token, config.jwt.secret) as JwtPayload;
  }

  static hasRole(userRole: UserRole, requiredRoles: UserRole[]): boolean {
    return requiredRoles.includes(userRole);
  }

  static isAdmin(userRole: UserRole): boolean {
    return userRole === UserRole.ADMIN;
  }

  static canAccess(userRole: UserRole, resourceRole: UserRole): boolean {
    const roleHierarchy = {
      [UserRole.ADMIN]: 4,
      [UserRole.MANAGER]: 3,
      [UserRole.USER]: 2,
      [UserRole.VIEWER]: 1,
    };

    return roleHierarchy[userRole] >= roleHierarchy[resourceRole];
  }
}

export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
};

export const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const calculatePagination = (page: number, limit: number, total: number) => {
  const pages = Math.ceil(total / limit);
  const hasNext = page < pages;
  const hasPrev = page > 1;

  return {
    page,
    limit,
    total,
    pages,
    hasNext,
    hasPrev,
  };
};