# API Contract: Backend Application Skeleton

**Parent**: [1.init-project](../../proposal.md)
**Created**: 2026-03-21

## Endpoints

### GET /api/health

**Description**: Health check endpoint to verify the application is running. Does not require database connectivity.

**Request**: No body or parameters.

**Response** (200):
```json
{
  "status": "ok"
}
```

**Error Responses**:
- 500: Application is not running or has a fatal startup error

## Out of Scope

- Authentication endpoints
- User management endpoints
- Database health checks

## Authentication

None required -- health check is public.

## Rate Limiting

No rate limiting on health check.
