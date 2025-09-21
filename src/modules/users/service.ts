import { User, CreateUserDto, UpdateUserDto, UserRole, AuthTokens, SearchQuery, PaginatedResponse } from '../../types';
import { AuthUtils, generateId, calculatePagination } from '../../utils/helpers';
import { AppError } from '../../middleware/errorHandler';
import logger from '../../utils/logger';

// In-memory storage for demonstration (replace with database in production)
class UserStorage {
  private users: Map<string, User & { password: string }> = new Map();

  async create(userData: CreateUserDto): Promise<User & { password: string }> {
    const id = generateId();
    const hashedPassword = await AuthUtils.hashPassword(userData.password);
    
    const user = {
      id,
      email: userData.email,
      username: userData.username,
      firstName: userData.firstName,
      lastName: userData.lastName,
      role: userData.role || UserRole.USER,
      isActive: true,
      password: hashedPassword,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.users.set(id, user);
    return user;
  }

  async findByEmail(email: string): Promise<(User & { password: string }) | null> {
    for (const user of this.users.values()) {
      if (user.email === email) {
        return user;
      }
    }
    return null;
  }

  async findByUsername(username: string): Promise<(User & { password: string }) | null> {
    for (const user of this.users.values()) {
      if (user.username === username) {
        return user;
      }
    }
    return null;
  }

  async findById(id: string): Promise<(User & { password: string }) | null> {
    return this.users.get(id) || null;
  }

  async update(id: string, updateData: UpdateUserDto): Promise<(User & { password: string }) | null> {
    const user = this.users.get(id);
    if (!user) return null;

    const updatedUser = {
      ...user,
      ...updateData,
      updatedAt: new Date(),
    };

    this.users.set(id, updatedUser);
    return updatedUser;
  }

  async delete(id: string): Promise<boolean> {
    return this.users.delete(id);
  }

  async findAll(query: SearchQuery): Promise<{ users: (User & { password: string })[]; total: number }> {
    let users = Array.from(this.users.values());

    // Search functionality
    if (query.q) {
      const searchTerm = query.q.toLowerCase();
      users = users.filter(user => 
        user.email.toLowerCase().includes(searchTerm) ||
        user.username.toLowerCase().includes(searchTerm) ||
        user.firstName.toLowerCase().includes(searchTerm) ||
        user.lastName.toLowerCase().includes(searchTerm)
      );
    }

    // Filtering
    if (query.filters) {
      if (query.filters.role) {
        users = users.filter(user => user.role === query.filters!.role);
      }
      if (query.filters.isActive !== undefined) {
        users = users.filter(user => user.isActive === query.filters!.isActive);
      }
    }

    // Sorting
    if (query.sortBy) {
      const sortOrder = query.sortOrder === 'asc' ? 1 : -1;
      users.sort((a, b) => {
        const aValue = (a as any)[query.sortBy!];
        const bValue = (b as any)[query.sortBy!];
        
        if (aValue < bValue) return -1 * sortOrder;
        if (aValue > bValue) return 1 * sortOrder;
        return 0;
      });
    }

    const total = users.length;
    
    // Pagination
    const page = query.page || 1;
    const limit = query.limit || 20;
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    
    users = users.slice(startIndex, endIndex);

    return { users, total };
  }

  async updateLastLogin(id: string): Promise<void> {
    const user = this.users.get(id);
    if (user) {
      user.lastLogin = new Date();
      user.updatedAt = new Date();
      this.users.set(id, user);
    }
  }

  async getAnalytics(): Promise<any> {
    const users = Array.from(this.users.values());
    
    const totalUsers = users.length;
    const activeUsers = users.filter(user => user.isActive).length;
    const inactiveUsers = totalUsers - activeUsers;
    
    const roleDistribution = users.reduce((acc, user) => {
      acc[user.role] = (acc[user.role] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const recentRegistrations = users.filter(user => {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      return user.createdAt >= thirtyDaysAgo;
    }).length;

    return {
      totalUsers,
      activeUsers,
      inactiveUsers,
      roleDistribution,
      recentRegistrations,
    };
  }
}

export class UserService {
  private userStorage: UserStorage;

  constructor() {
    this.userStorage = new UserStorage();
  }

  async createUser(userData: CreateUserDto): Promise<{ user: Omit<User, 'password'>; tokens: AuthTokens }> {
    // Check if user already exists
    const existingUserByEmail = await this.userStorage.findByEmail(userData.email);
    if (existingUserByEmail) {
      throw new AppError('User with this email already exists', 409);
    }

    const existingUserByUsername = await this.userStorage.findByUsername(userData.username);
    if (existingUserByUsername) {
      throw new AppError('User with this username already exists', 409);
    }

    const user = await this.userStorage.create(userData);
    
    // Generate tokens
    const tokens = {
      accessToken: AuthUtils.generateAccessToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      }),
      refreshToken: AuthUtils.generateRefreshToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      }),
    };

    const { password, ...userWithoutPassword } = user;

    logger.info(`User created: ${user.email}`);

    return {
      user: userWithoutPassword,
      tokens,
    };
  }

  async loginUser(email: string, password: string): Promise<{ user: Omit<User, 'password'>; tokens: AuthTokens }> {
    const user = await this.userStorage.findByEmail(email);
    if (!user) {
      throw new AppError('Invalid email or password', 401);
    }

    if (!user.isActive) {
      throw new AppError('Account is deactivated', 401);
    }

    const isPasswordValid = await AuthUtils.comparePassword(password, user.password);
    if (!isPasswordValid) {
      throw new AppError('Invalid email or password', 401);
    }

    // Update last login
    await this.userStorage.updateLastLogin(user.id);

    // Generate tokens
    const tokens = {
      accessToken: AuthUtils.generateAccessToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      }),
      refreshToken: AuthUtils.generateRefreshToken({
        userId: user.id,
        email: user.email,
        role: user.role,
      }),
    };

    const { password: _, ...userWithoutPassword } = user;

    logger.info(`User logged in: ${user.email}`);

    return {
      user: userWithoutPassword,
      tokens,
    };
  }

  async getUserById(id: string): Promise<Omit<User, 'password'>> {
    const user = await this.userStorage.findById(id);
    if (!user) {
      throw new AppError('User not found', 404);
    }

    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  async updateUser(id: string, updateData: UpdateUserDto): Promise<Omit<User, 'password'>> {
    // Check if email is being updated and if it already exists
    if (updateData.email) {
      const existingUser = await this.userStorage.findByEmail(updateData.email);
      if (existingUser && existingUser.id !== id) {
        throw new AppError('Email already in use', 409);
      }
    }

    // Check if username is being updated and if it already exists
    if (updateData.username) {
      const existingUser = await this.userStorage.findByUsername(updateData.username);
      if (existingUser && existingUser.id !== id) {
        throw new AppError('Username already in use', 409);
      }
    }

    const updatedUser = await this.userStorage.update(id, updateData);
    if (!updatedUser) {
      throw new AppError('User not found', 404);
    }

    const { password, ...userWithoutPassword } = updatedUser;

    logger.info(`User updated: ${updatedUser.email}`);

    return userWithoutPassword;
  }

  async deleteUser(id: string): Promise<void> {
    const user = await this.userStorage.findById(id);
    if (!user) {
      throw new AppError('User not found', 404);
    }

    await this.userStorage.delete(id);

    logger.info(`User deleted: ${user.email}`);
  }

  async getAllUsers(query: SearchQuery): Promise<PaginatedResponse<Omit<User, 'password'>>> {
    const { users, total } = await this.userStorage.findAll(query);
    
    const usersWithoutPassword = users.map(user => {
      const { password, ...userWithoutPassword } = user;
      return userWithoutPassword;
    });

    const pagination = calculatePagination(query.page || 1, query.limit || 20, total);

    return {
      data: usersWithoutPassword,
      pagination,
    };
  }

  async getUserAnalytics(): Promise<any> {
    return this.userStorage.getAnalytics();
  }
}