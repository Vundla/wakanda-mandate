import { Router } from 'express';
import { UserController } from './controller';
import { authenticate, authorize } from '../../middleware/auth';
import { validateRequest, validateQuery } from '../../middleware/validation';
import { userValidationSchemas, searchValidationSchema } from '../../utils/validation';
import { UserRole } from '../../types';

const router = Router();
const userController = new UserController();

// Public routes
router.post('/register', validateRequest(userValidationSchemas.create), userController.register);
router.post('/login', validateRequest(userValidationSchemas.login), userController.login);

// Protected routes
router.get('/profile', authenticate, userController.getProfile);
router.put('/profile', authenticate, validateRequest(userValidationSchemas.update), userController.updateProfile);

// Admin routes
router.get('/', authenticate, authorize([UserRole.ADMIN]), validateQuery(searchValidationSchema), userController.getUsers);
router.get('/analytics', authenticate, authorize([UserRole.ADMIN]), userController.getAnalytics);
router.get('/:id', authenticate, authorize([UserRole.ADMIN, UserRole.MANAGER]), userController.getUserById);
router.put('/:id', authenticate, authorize([UserRole.ADMIN]), validateRequest(userValidationSchemas.update), userController.updateUser);
router.delete('/:id', authenticate, authorize([UserRole.ADMIN]), userController.deleteUser);

// Health check
router.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'Users module is healthy',
    timestamp: new Date(),
  });
});

export default router;