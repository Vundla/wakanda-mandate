import { Router } from 'express';

const router = Router();

// Placeholder endpoints
router.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'Policy module is healthy',
    timestamp: new Date(),
  });
});

router.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Policy module - Coming soon',
    timestamp: new Date(),
  });
});

export default router;