import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

import { config } from './config';
import logger from './utils/logger';
import { errorHandler, notFoundHandler } from './middleware/errorHandler';

// Import route modules
import userRoutes from './modules/users/routes';
import jobRoutes from './modules/jobs/routes';
import financeRoutes from './modules/finance/routes';
import energyRoutes from './modules/energy/routes';
import carbonRoutes from './modules/carbon/routes';
import aiRoutes from './modules/ai/routes';
import policyRoutes from './modules/policy/routes';

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: config.app.corsOrigin,
  credentials: true,
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  message: {
    success: false,
    error: 'Too many requests, please try again later',
    timestamp: new Date(),
  },
});
app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Swagger documentation
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Wakanda Mandate API',
      version: '1.0.0',
      description: 'Comprehensive enterprise API for Wakanda Mandate application',
    },
    servers: [
      {
        url: `http://localhost:${config.app.port}`,
        description: 'Development server',
      },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        },
      },
    },
    security: [
      {
        bearerAuth: [],
      },
    ],
  },
  apis: ['./src/modules/*/routes.ts', './src/modules/*/controller.ts'],
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'Wakanda Mandate API is running',
    timestamp: new Date(),
    version: '1.0.0',
    environment: config.app.nodeEnv,
  });
});

// API routes
app.use('/api/users', userRoutes);
app.use('/api/jobs', jobRoutes);
app.use('/api/finance', financeRoutes);
app.use('/api/energy', energyRoutes);
app.use('/api/carbon', carbonRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/policy', policyRoutes);

// Error handling middleware (must be last)
app.use(notFoundHandler);
app.use(errorHandler);

export default app;