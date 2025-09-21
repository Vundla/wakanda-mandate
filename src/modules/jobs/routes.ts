import { Router } from 'express';

const router = Router();

// Placeholder endpoints - will be implemented next
router.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'Jobs module is healthy',
    timestamp: new Date(),
  });
});

router.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Jobs module - Coming soon',
    timestamp: new Date(),
  });
});

export default router;