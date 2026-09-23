# Design Notes

## Database Schema and Normalization

The platform uses PostgreSQL with separate Users, Sessions, and Evaluations tables. Users contain identity, authentication, and role information, while Sessions reference a teacher and a child through foreign keys. Evaluations reference Sessions rather than duplicating session information.

This structure follows normalization principles by keeping each entity's data in its own table and avoiding repeated attributes. Foreign keys maintain referential integrity between related records. A self-referencing relationship on Users allows a parent to be associated with one or more child accounts. In a larger production system, a dedicated Children/Students table could also be introduced if children require attributes different from authenticated users.

Indexes should be added to frequently filtered columns such as session teacher_id, child_id, and evaluation session_id as the dataset grows.

## RBAC Evolution

The current system supports admin, teacher, parent, and student roles. Teachers can access only sessions assigned to them, while parents can access sessions belonging to their own children. Admins have broader access.

If a fourth operational role is introduced, role permissions should be separated from route implementation. A permission-based model can map roles to permissions such as `session:read`, `session:create`, and `evaluation:trigger`.

For nested organizations, additional Organization and Membership tables can be introduced. A membership would associate a user with an organization and define their role or permissions within that organization. Authorization would then consider both the user's permissions and the organization/resource relationship.

## Production Safety

Secrets such as JWT keys and database credentials should be supplied through environment variables or a dedicated secret manager rather than committed to source control. Production traffic should use HTTPS, and JWT secrets should be rotated securely.

Database schema changes should be managed exclusively through Alembic migrations. Redis should use authentication and appropriate network restrictions in production.

The evaluation endpoint currently places work onto a Redis queue. A production worker should consume this queue with retry handling, idempotency, and dead-letter handling for failed jobs. API rate limiting, structured logging, monitoring, health checks, input validation, database connection pooling, and automated tests should also be enabled before production deployment.

Docker images and dependencies should be pinned to controlled versions, and application containers should run with minimal privileges.