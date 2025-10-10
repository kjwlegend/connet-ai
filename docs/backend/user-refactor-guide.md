# User Refactor Guide

## Context & Current State
- `bff/app/infrastructure/database/models/user_model.py` currently mixes authentication, growth, engagement, and analytics concerns in a single table with ~40 columns, most of them JSON blobs (`preferences`, `permissions`, `roles`, `user_metadata`).
- Invitation, telemetry, and per-app profile data share the same table, which makes it difficult to scope data to a specific client app or feature set and introduces wide-row performance issues.
- Role and permission management is persisted as free-form JSON arrays, preventing relational integrity, reuse across apps, or enforcement of RBAC constraints.
- The repository (`bff/app/infrastructure/database/repositories/user_repository_impl.py`) writes raw passwords into `password_hash` when a hashed value is not provided and does not normalize identifiers (e.g., treating UUIDs as strings), which is risky for security and data consistency.
- Global unique constraints on fields such as `username` and `invitation_code` prevent the same person from having different personas per app or environment.

## Confirmed Assumptions
- Identity is shared across multiple consumer apps; we will **not** implement multi-tenant/org scoping in this phase.
- Authentication providers to support from day one: Supabase, Google OAuth, GitHub OAuth.
- Invitation flows are scoped per app (each `user_app_account` manages its own invite codes and referral metrics).
- We will launch on a brand-new database; historical migrations/backfills are unnecessary during the initial rollout.

## Should We Create a Separate Admin User?
- **Recommendation:** keep administrators in the same `users` table and drive elevated access through RBAC. A distinct admin table would duplicate profile fields, invite inconsistent onboarding paths, and complicate cross-app SSO.
- Introduce an `admin_profiles` (or `staff_profiles`) table only if the management console needs metadata that should never exist for consumer accounts (e.g., staffing notes, support shift assignments). This allows admin-only attributes without fragmenting identity.

## Target Data Model

### Identity & Authentication
- **users**: canonical identity (UUID PK, email, password_hash, primary_full_name, primary_avatar, status flags, verified_at, created_at/updated_at).
- **user_auth_identities**: supports multiple providers per user (`user_id`, `provider` enum, `provider_user_id`, `access_token`, `refresh_token`, `expires_at`, `metadata`).

### Application Membership & Profiles
- **client_apps**: registry of C-end apps and internal surfaces (`id`, `key`, `name`, `type`, `status`, `metadata`).
- **user_app_accounts**: bridges `users` to each `client_app` (`id`, `user_id`, `app_id`, `app_scoped_username`, `display_name`, `avatar_url`, `profile`, `preferences`, `invitation_code`, `status`, timestamps). This is where per-app stats (message counts, rewards) should live.
- **user_app_settings** (optional): JSON settings per app & user, allowing typed schemas without overloading the account table.

### Authorization & Groups
- **roles**: (`id`, `scope` = `global | app | group`, `name`, `slug`, `description`).
- **permissions**: (`id`, `key`, `description`, `metadata`).
- **role_permissions**: (`role_id`, `permission_id`).
- **user_roles**: (`user_id`, `role_id`, `app_id?`, `granted_by`, `granted_at`, `expires_at`).
- **groups**: (`id`, `app_id` nullable for global/admin, `name`, `slug`, `type`, `metadata`).
- **group_members**: (`group_id`, `user_id`, `app_id`, `joined_at`, `status`).
- **group_roles**: assigns RBAC bundles to groups (`group_id`, `role_id`).

### Auditing & Growth
- **user_invites**: replace invitation columns in `users` with a dedicated table capturing inviter, invitee, campaign, usage counts, and reward events (scoped by `app_id`).
- **user_activity_metrics**: optional aggregate table for cross-app reporting (daily stats keyed by `user_id`, `app_id`, `metric_date`).

### Relationships Overview
```
users ──< user_auth_identities
users ──< user_app_accounts >── client_apps
users ──< user_roles >── roles >── role_permissions >── permissions
users ──< group_members >── groups
groups ──< group_roles >── roles
users ──< user_invites
```

## Code & Schema Refactor Plan
1. **Extract canonical identity:** Slim `UserModel` to identity-only fields (email, password_hash, full_name, status, timestamps). Move engagement metrics, invitation stats, and profile metadata to purpose-built tables.
2. **Normalize auth providers:** Implement `UserAuthIdentityModel` and update Supabase/auth flows to store provider IDs separately from the core user row.
3. **Introduce app-level accounts:** Create `ClientAppModel` and `UserAppAccountModel` with uniqueness scoped to `(app_id, app_scoped_username)` and `(app_id, invitation_code)`. Update repositories/services to require an `app_id` when creating or querying per-app data and ensure invite logic lives at the app level.
4. **Implement RBAC schema:** Replace JSON `roles`/`permissions` with relational tables. Add service abstractions in `app/core/` for role assignment and permission checks so API code no longer inspects JSON fields.
5. **Admin backend alignment:** Seed global roles such as `platform.admin`, `platform.support`, `app.moderator`, and create group structures for admin teams. Introduce `AdminProfileModel` only if admin-only metadata is required.
6. **Repository & service updates:** Split the current `UserRepository` into identity, account, and membership repositories (e.g., `IdentityRepository`, `AppAccountRepository`). Ensure password handling always hashes via a domain service before persistence.
7. **API layer adjustments:** Update Pydantic schemas to reflect the new structure (`UserIdentityResponse`, `UserAppAccountResponse`, `RoleAssignmentResponse`). Provide migration-friendly DTOs for legacy endpoints during rollout.
8. **Initial schema setup:** Author Alembic (or SQLModel metadata) definitions for the new tables and seed baseline data (apps, roles, permissions) for the greenfield database. Backfill scripts are optional now but document how to support them later.
9. **Testing & validation:** Add coverage for multi-app login flows, RBAC enforcement, and provider sync (Supabase, Google, GitHub) in `tests/`. Ensure fixtures cover admin and consumer scenarios.

## Identified Issues & Recommended Fixes
- Replace JSON `roles`/`permissions` fields with relational tables to support complex authorization and auditing.
- Prevent plaintext password storage by enforcing hashing in the service layer before repository writes.
- Remove global uniqueness on `username` and `invitation_code`; scope them to `(app_id, ...)` combinations to enable per-app personas.
- Stop overloading the user table with engagement metrics; this data belongs in derived tables (`user_app_stats`, activity logs) to keep the identity row lean.
- Introduce lifecycle triggers (SQLAlchemy events or explicit service logic) to maintain `updated_at` and `last_login_at` without manual assignment in multiple code paths.
- Validate UUID handling in repositories—favor `UUID` objects end-to-end to avoid accidental string comparisons and to keep type checking effective under mypy strict mode.

## Remaining Open Questions
- Do admin/staff accounts require additional immutable metadata (e.g., staff IDs, department) that justify an `admin_profiles` table, or can we keep everything in roles/groups?
- Should app-level stats be aggregated nightly into `user_activity_metrics` or derived on the fly from event stores? Define requirements before implementing the analytics layer.

## Next Steps
1. Finalize admin metadata needs and analytics aggregation requirements.
2. Split the implementation work into: schema creation (initial Alembic revisions), repository/service refactor, and API adjustments.
3. Prototype the new tables in a feature branch, generate the initial migration to create the schema from scratch, and iterate before integrating with the frontend and auth flows.

## TODO Checklist
- [ ] Sketch ER diagrams for the new tables (`users`, `user_auth_identities`, `client_apps`, `user_app_accounts`, `roles`, `permissions`, etc.) and validate cardinalities.
- [ ] Define enums/constants for auth providers (`supabase`, `google`, `github`) and role scopes (`global`, `app`, `group`).
- [ ] Specify JSON schema (or typed models) for `user_app_accounts.profile` and `user_app_accounts.preferences` to keep per-app profiles consistent.
- [ ] Draft repository interfaces for identity, app accounts, roles/permissions, and invitations within the upcoming `modules/users` vertical slice.
- [ ] Update authentication services (Supabase, OAuth) to populate `user_auth_identities` and per-app accounts, ensuring invite codes are generated per app.
- [ ] Plan seed data for default apps, roles, and permissions to bootstrap a fresh environment.
- [ ] Align API schemas and routers with the new structure, including admin-facing endpoints for role assignment and invite management.
