export interface User {
  id: string;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastLogin?: Date;
}

export interface CreateUserDto {
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  password: string;
  role?: UserRole;
}

export interface UpdateUserDto {
  email?: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role?: UserRole;
  isActive?: boolean;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface JwtPayload {
  userId: string;
  email: string;
  role: UserRole;
  iat?: number;
  exp?: number;
}

export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  USER = 'user',
  VIEWER = 'viewer'
}

export interface Job {
  id: string;
  title: string;
  description: string;
  department: string;
  location: string;
  salary: {
    min: number;
    max: number;
    currency: string;
  };
  requirements: string[];
  benefits: string[];
  status: JobStatus;
  postedBy: string;
  applicants: string[];
  createdAt: Date;
  updatedAt: Date;
  closingDate?: Date;
}

export enum JobStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  CLOSED = 'closed',
  FILLED = 'filled'
}

export interface FinanceRecord {
  id: string;
  category: FinanceCategory;
  amount: number;
  currency: string;
  description: string;
  date: Date;
  quarter: string;
  year: number;
  department?: string;
  projectId?: string;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export enum FinanceCategory {
  REVENUE = 'revenue',
  EXPENSE = 'expense',
  INVESTMENT = 'investment',
  PROFIT = 'profit',
  LOSS = 'loss'
}

export interface EnergyData {
  id: string;
  source: EnergySource;
  consumption: number;
  unit: EnergyUnit;
  cost: number;
  currency: string;
  location: string;
  timestamp: Date;
  efficiency?: number;
  emissions?: number;
  createdAt: Date;
  updatedAt: Date;
}

export enum EnergySource {
  SOLAR = 'solar',
  WIND = 'wind',
  HYDRO = 'hydro',
  NUCLEAR = 'nuclear',
  COAL = 'coal',
  GAS = 'gas',
  OTHER = 'other'
}

export enum EnergyUnit {
  KWH = 'kWh',
  MWH = 'MWh',
  GWH = 'GWh'
}

export interface CarbonFootprint {
  id: string;
  activity: string;
  category: CarbonCategory;
  emissions: number;
  unit: CarbonUnit;
  scope: CarbonScope;
  date: Date;
  location?: string;
  department?: string;
  description?: string;
  calculationMethod: string;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export enum CarbonCategory {
  ENERGY = 'energy',
  TRANSPORT = 'transport',
  WASTE = 'waste',
  WATER = 'water',
  MATERIALS = 'materials',
  OTHER = 'other'
}

export enum CarbonUnit {
  CO2E_KG = 'kg CO2e',
  CO2E_TON = 'ton CO2e'
}

export enum CarbonScope {
  SCOPE_1 = 'scope1',
  SCOPE_2 = 'scope2',
  SCOPE_3 = 'scope3'
}

export interface AIChat {
  id: string;
  userId: string;
  sessionId: string;
  messages: ChatMessage[];
  model: string;
  totalTokens: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  tokens?: number;
}

export interface Policy {
  id: string;
  title: string;
  content: string;
  category: PolicyCategory;
  version: string;
  status: PolicyStatus;
  effectiveDate: Date;
  expiryDate?: Date;
  approvedBy: string;
  tags: string[];
  attachments?: string[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export enum PolicyCategory {
  HR = 'hr',
  FINANCE = 'finance',
  SECURITY = 'security',
  ENVIRONMENTAL = 'environmental',
  OPERATIONAL = 'operational',
  LEGAL = 'legal'
}

export enum PolicyStatus {
  DRAFT = 'draft',
  REVIEW = 'review',
  APPROVED = 'approved',
  ACTIVE = 'active',
  ARCHIVED = 'archived'
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: Date;
  path: string;
  method: string;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface SearchQuery {
  q?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
}