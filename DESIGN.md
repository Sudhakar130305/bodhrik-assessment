#  System Design and Architecture Notes

## Database Schema and Normalization

The platform uses PostgreSQL with separate `Users`, `Sessions`, and `Evaluations` tables. Users store identity, authentication, and role information. Sessions reference the teacher and child through foreign keys, while evaluations reference a session instead of duplicating session data. This keeps each entity focused on one responsibility and avoids repeated attributes.

The schema is intentionally normalized around these core relationships. A session stores `teacher_id` and `child_id` rather than copying teacher or child details, so changes to user information do not require updates across multiple session records. The parent-child relationship is represented through a self-referencing relationship on `Users`, which keeps the initial schema small and avoids an additional mapping table. The tradeoff is that this relationship is less flexible if the product later supports multiple guardians, complex family relationships, or children who are not represented as authenticated users. At that stage, a dedicated `Children/Students` table or a separate relationship table would be more appropriate. Indexes on frequently filtered foreign keys such as `teacher_id`, `child_id`, and `evaluation.session_id` should also be maintained as the dataset grows.

## RBAC Evolution

The current implementation supports `admin`, `teacher`, `parent`, and `student` roles. Authorization is enforced at the API layer and also checks resource ownership: teachers can access only their own sessions, parents can access sessions belonging to their children, and administrators have broader access.

If another operational role is introduced, permissions should be separated from route-specific logic. Instead of hard-coding every role into endpoints, a permission-based model could map roles to permissions such as `session:read`, `session:create`, and `evaluation:trigger`. For nested organizations, the schema would need `Organization` and `Membership` tables. A membership could associate a user with an organization and define their role or permissions within that organization. Authorization would then evaluate both the user's permissions and the organization/resource relationship.

## Production Safety

This assessment is designed as a functional prototype, so several production controls would still be required. Database schema changes should be managed through versioned Alembic migrations, with migrations reviewed and applied through a controlled deployment process. Secrets such as JWT keys and database credentials should come from environment variables or a dedicated secret manager and must not be committed to source control.

Production traffic should use HTTPS, JWT secrets should be rotated securely, and Redis should have authentication and network restrictions. The evaluation endpoint currently places jobs on a Redis queue; production would require a dedicated worker with retry handling, idempotency, and dead-letter handling so failed evaluations are not silently lost or processed incorrectly.

Additional production safeguards would include API rate limiting, structured logging, monitoring and alerting, health checks, stronger input validation, database connection pooling, comprehensive automated tests, dependency and Docker image pinning, and least-privilege container execution. These changes would make the system safer and more operationally reliable without changing the core data model.