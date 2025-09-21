import Joi from 'joi';
import { UserRole } from '../types';

export const userValidationSchemas = {
  create: Joi.object({
    email: Joi.string().email().required(),
    username: Joi.string().alphanum().min(3).max(30).required(),
    firstName: Joi.string().min(2).max(50).required(),
    lastName: Joi.string().min(2).max(50).required(),
    password: Joi.string().min(8).pattern(new RegExp('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\\$%\\^&\\*])')).required()
      .messages({
        'string.pattern.base': 'Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character'
      }),
    role: Joi.string().valid(...Object.values(UserRole)).optional().default(UserRole.USER),
  }),

  update: Joi.object({
    email: Joi.string().email().optional(),
    username: Joi.string().alphanum().min(3).max(30).optional(),
    firstName: Joi.string().min(2).max(50).optional(),
    lastName: Joi.string().min(2).max(50).optional(),
    role: Joi.string().valid(...Object.values(UserRole)).optional(),
    isActive: Joi.boolean().optional(),
  }),

  login: Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().required(),
  }),
};

export const jobValidationSchemas = {
  create: Joi.object({
    title: Joi.string().min(5).max(100).required(),
    description: Joi.string().min(20).max(2000).required(),
    department: Joi.string().min(2).max(50).required(),
    location: Joi.string().min(2).max(100).required(),
    salary: Joi.object({
      min: Joi.number().positive().required(),
      max: Joi.number().positive().greater(Joi.ref('min')).required(),
      currency: Joi.string().length(3).uppercase().required(),
    }).required(),
    requirements: Joi.array().items(Joi.string()).min(1).required(),
    benefits: Joi.array().items(Joi.string()).optional(),
    closingDate: Joi.date().greater('now').optional(),
  }),

  update: Joi.object({
    title: Joi.string().min(5).max(100).optional(),
    description: Joi.string().min(20).max(2000).optional(),
    department: Joi.string().min(2).max(50).optional(),
    location: Joi.string().min(2).max(100).optional(),
    salary: Joi.object({
      min: Joi.number().positive().optional(),
      max: Joi.number().positive().optional(),
      currency: Joi.string().length(3).uppercase().optional(),
    }).optional(),
    requirements: Joi.array().items(Joi.string()).optional(),
    benefits: Joi.array().items(Joi.string()).optional(),
    status: Joi.string().valid('draft', 'published', 'closed', 'filled').optional(),
    closingDate: Joi.date().optional(),
  }),
};

export const financeValidationSchemas = {
  create: Joi.object({
    category: Joi.string().valid('revenue', 'expense', 'investment', 'profit', 'loss').required(),
    amount: Joi.number().required(),
    currency: Joi.string().length(3).uppercase().required(),
    description: Joi.string().min(5).max(500).required(),
    date: Joi.date().required(),
    department: Joi.string().optional(),
    projectId: Joi.string().optional(),
  }),
};

export const energyValidationSchemas = {
  create: Joi.object({
    source: Joi.string().valid('solar', 'wind', 'hydro', 'nuclear', 'coal', 'gas', 'other').required(),
    consumption: Joi.number().positive().required(),
    unit: Joi.string().valid('kWh', 'MWh', 'GWh').required(),
    cost: Joi.number().positive().required(),
    currency: Joi.string().length(3).uppercase().required(),
    location: Joi.string().min(2).max(100).required(),
    timestamp: Joi.date().required(),
    efficiency: Joi.number().min(0).max(100).optional(),
    emissions: Joi.number().min(0).optional(),
  }),
};

export const carbonValidationSchemas = {
  create: Joi.object({
    activity: Joi.string().min(3).max(100).required(),
    category: Joi.string().valid('energy', 'transport', 'waste', 'water', 'materials', 'other').required(),
    emissions: Joi.number().positive().required(),
    unit: Joi.string().valid('kg CO2e', 'ton CO2e').required(),
    scope: Joi.string().valid('scope1', 'scope2', 'scope3').required(),
    date: Joi.date().required(),
    location: Joi.string().optional(),
    department: Joi.string().optional(),
    description: Joi.string().max(500).optional(),
    calculationMethod: Joi.string().min(5).max(200).required(),
  }),
};

export const policyValidationSchemas = {
  create: Joi.object({
    title: Joi.string().min(5).max(200).required(),
    content: Joi.string().min(50).required(),
    category: Joi.string().valid('hr', 'finance', 'security', 'environmental', 'operational', 'legal').required(),
    version: Joi.string().pattern(/^\d+\.\d+\.\d+$/).required(),
    effectiveDate: Joi.date().required(),
    expiryDate: Joi.date().greater(Joi.ref('effectiveDate')).optional(),
    tags: Joi.array().items(Joi.string()).optional(),
    attachments: Joi.array().items(Joi.string()).optional(),
  }),

  update: Joi.object({
    title: Joi.string().min(5).max(200).optional(),
    content: Joi.string().min(50).optional(),
    category: Joi.string().valid('hr', 'finance', 'security', 'environmental', 'operational', 'legal').optional(),
    version: Joi.string().pattern(/^\d+\.\d+\.\d+$/).optional(),
    status: Joi.string().valid('draft', 'review', 'approved', 'active', 'archived').optional(),
    effectiveDate: Joi.date().optional(),
    expiryDate: Joi.date().optional(),
    tags: Joi.array().items(Joi.string()).optional(),
    attachments: Joi.array().items(Joi.string()).optional(),
  }),
};

export const searchValidationSchema = Joi.object({
  q: Joi.string().optional(),
  page: Joi.number().integer().min(1).optional().default(1),
  limit: Joi.number().integer().min(1).max(100).optional().default(20),
  sortBy: Joi.string().optional(),
  sortOrder: Joi.string().valid('asc', 'desc').optional().default('desc'),
  filters: Joi.object().optional(),
});