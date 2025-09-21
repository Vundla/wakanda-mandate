import { Request, Response } from 'express';
import { AuthenticatedRequest } from '../../middleware/auth';
import { UserService } from './service';
import { asyncHandler } from '../../middleware/errorHandler';
import { CreateUserDto, UpdateUserDto, UserRole } from '../../types';

export class UserController {
  private userService: UserService;

  constructor() {
    this.userService = new UserService();
  }

  /**
   * @swagger
   * /api/users/register:
   *   post:
   *     summary: Register a new user
   *     tags: [Users]
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - email
   *               - username
   *               - firstName
   *               - lastName
   *               - password
   *             properties:
   *               email:
   *                 type: string
   *                 format: email
   *               username:
   *                 type: string
   *               firstName:
   *                 type: string
   *               lastName:
   *                 type: string
   *               password:
   *                 type: string
   *                 minLength: 8
   *               role:
   *                 type: string
   *                 enum: [admin, manager, user, viewer]
   */
  register = asyncHandler(async (req: Request, res: Response) => {
    const userData: CreateUserDto = req.body;
    const result = await this.userService.createUser(userData);

    res.status(201).json({
      success: true,
      data: result,
      message: 'User registered successfully',
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users/login:
   *   post:
   *     summary: Login user
   *     tags: [Users]
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - email
   *               - password
   *             properties:
   *               email:
   *                 type: string
   *                 format: email
   *               password:
   *                 type: string
   */
  login = asyncHandler(async (req: Request, res: Response) => {
    const { email, password } = req.body;
    const result = await this.userService.loginUser(email, password);

    res.json({
      success: true,
      data: result,
      message: 'Login successful',
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users/profile:
   *   get:
   *     summary: Get current user profile
   *     tags: [Users]
   *     security:
   *       - bearerAuth: []
   */
  getProfile = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.userId;
    const user = await this.userService.getUserById(userId);

    res.json({
      success: true,
      data: user,
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users/profile:
   *   put:
   *     summary: Update current user profile
   *     tags: [Users]
   *     security:
   *       - bearerAuth: []
   */
  updateProfile = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.userId;
    const updateData: UpdateUserDto = req.body;
    const user = await this.userService.updateUser(userId, updateData);

    res.json({
      success: true,
      data: user,
      message: 'Profile updated successfully',
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users:
   *   get:
   *     summary: Get all users (Admin only)
   *     tags: [Users]
   *     security:
   *       - bearerAuth: []
   */
  getUsers = asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const users = await this.userService.getAllUsers(req.query);

    res.json({
      success: true,
      data: users,
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users/{id}:
   *   get:
   *     summary: Get user by ID
   *     tags: [Users]
   *     security:
   *       - bearerAuth: []
   *     parameters:
   *       - in: path
   *         name: id
   *         required: true
   *         schema:
   *           type: string
   */
  getUserById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const user = await this.userService.getUserById(id);

    res.json({
      success: true,
      data: user,
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users/{id}:
   *   put:
   *     summary: Update user by ID (Admin only)
   *     tags: [Users]
   *     security:
   *       - bearerAuth: []
   */
  updateUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const updateData: UpdateUserDto = req.body;
    const user = await this.userService.updateUser(id, updateData);

    res.json({
      success: true,
      data: user,
      message: 'User updated successfully',
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users/{id}:
   *   delete:
   *     summary: Delete user by ID (Admin only)
   *     tags: [Users]
   *     security:
   *       - bearerAuth: []
   */
  deleteUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    await this.userService.deleteUser(id);

    res.json({
      success: true,
      message: 'User deleted successfully',
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });

  /**
   * @swagger
   * /api/users/analytics:
   *   get:
   *     summary: Get user analytics (Admin only)
   *     tags: [Users]
   *     security:
   *       - bearerAuth: []
   */
  getAnalytics = asyncHandler(async (req: Request, res: Response) => {
    const analytics = await this.userService.getUserAnalytics();

    res.json({
      success: true,
      data: analytics,
      timestamp: new Date(),
      path: req.path,
      method: req.method,
    });
  });
}