# MoyoCare API contracts

This guide describes the backend API for the Android and web clients. The API base path is `/api/v1/`.

## Conventions

- Send and receive JSON using `Content-Type: application/json` and `Accept: application/json`.
- UUIDs are JSON strings. Timestamps are ISO 8601 values; send an explicit timezone for client-recorded times.
- Protected API routes require a MoyoCare JWT access token. Send it as `Authorization: Bearer <access-token>`. Token obtain and refresh are public routes.
- List routes use page-number pagination with a default page size of 25:

  ```json
  {
    "count": 47,
    "next": "https://api.example/api/v1/facilities/?page=2",
    "previous": null,
    "results": []
  }
  ```

- List routes accept `page`, `search`, and `ordering` where enabled. A leading `-` sorts descending, for example `?ordering=-created_at`.
- Validation failures return `400` with field-keyed messages. Missing/invalid credentials return `401`; authenticated users without permission receive `403`. A detail route outside the caller's facility scope returns `404`.
- Write access to organizations and facilities is limited to staff accounts. Patient and report access is limited to active facility members; staff accounts have access across facilities. Facility membership is provisioned in Django admin.

## Authentication and profile

### Sign in

`POST /api/v1/auth/token/`

```json
{"email":"hsa@example.org","password":"admin-issued-password"}
```

Returns `200` with `access` and `refresh` JWTs. Invalid credentials or inactive accounts return `401`. Administrators create the user account and provide the initial email and password; there is no public registration endpoint. Staff can change their password after signing in using the change-password endpoint below.

### Refresh tokens

`POST /api/v1/auth/token/refresh/`

```json
{"refresh":"<refresh-token>"}
```

Returns `200` with a new access token. Refresh-token rotation is enabled; save the returned refresh token when present.

### Get or update the signed-in user

- `GET /api/v1/auth/me/`
- `PATCH /api/v1/auth/me/`

Profile response fields are `id`, `email`, `first_name`, `last_name`, and `date_joined`. Only first and last name can be changed. ID, email, and join date are read-only.

```json
{"first_name":"Jane","last_name":"Banda"}
```

### Change password

`POST /api/v1/auth/change-password/`

```json
{
  "current_password":"current-password",
  "new_password":"new-password"
}
```

Returns `200` with `{"detail":"Password updated successfully."}`. An incorrect current password, a weak password, or reusing the current password returns `400`. Existing refresh tokens are revoked after a password change.

## Organizations

Collection: `/api/v1/organizations/`  
Detail: `/api/v1/organizations/{id}/`

| Method | Permission | Result |
| --- | --- | --- |
| `GET` collection/detail | Authenticated | List or retrieve |
| `POST` collection | Staff | Create, `201` |
| `PUT` / `PATCH` detail | Staff | Replace or update, `200` |
| `DELETE` detail | Staff | Delete, `204`; `409` if child organizations or facilities depend on it |

Writable fields:

| Field | Type | Notes |
| --- | --- | --- |
| `name` | string | Required; max 255 characters |
| `code` | slug string | Required and unique; max 50 characters |
| `organization_type` | enum | `ministry`, `district`, `partner`, `other`; defaults to `other` |
| `description` | string | Optional |
| `parent` | UUID or `null` | Optional parent organization; cycles are rejected |
| `is_active` | boolean | Defaults to `true` |

Response fields also include read-only `id`, `created_at`, and `updated_at`. Universities and research institutes can use `organization_type: "other"`.

Filters: `organization_type`, `parent`, `is_active`. Search: `name`, `code`, `description`. Ordering: `name`, `code`, `created_at`, `updated_at`.

## Facilities

Collection: `/api/v1/facilities/`  
Detail: `/api/v1/facilities/{id}/`

Authenticated users can read facilities assigned to them. Staff can read all facilities and perform writes.

| Method | Permission | Result |
| --- | --- | --- |
| `GET` collection/detail | Authenticated and in scope | List or retrieve |
| `POST` collection | Staff | Create, `201` |
| `PUT` / `PATCH` detail | Staff | Replace or update, `200` |
| `DELETE` detail | Staff | Delete, `204`; `409` when patients or memberships depend on it |

Writable fields are `organization` (required organization UUID), `name` (required, max 255), `code` (required unique slug, max 50), `facility_type`, `district`, `community`, `address`, `phone_number`, and `is_active`.

Facility types: `hospital`, `health_centre`, `clinic`, `dispensary`, `community`, `other`. The default is `other`. `district`, `community`, `address`, and `phone_number` may be empty. Response fields also include read-only `id`, `created_at`, and `updated_at`.

Filters: `organization`, `facility_type`, `district`, `community`, `is_active`. Search: `name`, `code`, `district`, `community`, `address`. Ordering: `name`, `code`, `district`, `created_at`, `updated_at`.

Membership roles currently are `health_worker` and `supervisor`; both have the same facility-level API permissions. Memberships are assigned through Django admin, not a public API.

## Patients

Collection: `/api/v1/patients/`  
Detail: `/api/v1/patients/{id}/`

Methods: `GET`, `POST`, `PUT`, and `PATCH`. Patient deletion is disabled; set `is_active` to `false` to deactivate a profile. The ID is a server-generated UUID on this resource.

Writable fields: `facility` (required UUID), `first_name` (required, max 150), `last_name` (required, max 150), `age` (optional integer from 0 to 120 or `null`), `gender` (`female`, `male`, `other`, `unknown`; defaults to `unknown`), `village` (optional, max 120), and `is_active` (defaults to `true`). The response also contains computed `name`, plus read-only `id`, `created_at`, and `updated_at`.

Example:

```json
{
  "facility":"13e10af4-610b-4a81-9e47-e9a3f415208c",
  "first_name":"Jane",
  "last_name":"Banda",
  "age":34,
  "gender":"female",
  "village":"Chilinde"
}
```

Filters: `facility`, `gender`, `village`, `is_active`. Search: `first_name`, `last_name`, `village`, and facility name. Ordering: `first_name`, `last_name`, `age`, `created_at`, `updated_at`.

## Patient reports / encounters

Collection: `/api/v1/patient-reports/`  
Detail: `/api/v1/patient-reports/{id}/`

Methods: authenticated `GET` list/detail and `POST` create. Reports are immutable through the API. Submissions can reference an existing patient UUID or include a new nested patient identity. A new nested profile and its first report are created atomically.

### Create a report

`POST /api/v1/patient-reports/`

```json
{
  "client_id":"2bd4f2bd-b7a0-460c-9db0-e58108fb22e0",
  "patient":{
    "id":"bf9886a3-8d6a-49bb-b865-79013b7de4b9",
    "facility":"13e10af4-610b-4a81-9e47-e9a3f415208c",
    "first_name":"Jane",
    "last_name":"Banda",
    "village":"Chilinde"
  },
  "age":34,
  "gender":"female",
  "symptoms":["fever","cough"],
  "action_taken":"Given paracetamol; referred to health centre",
  "occurred_at":"2026-11-11T08:30:00+02:00"
}
```

For an existing patient, `patient` can instead be the UUID string. The nested identity object requires a client-generated `id`, an assigned active `facility`, `first_name`, and `last_name`; `village` is optional. If that UUID already exists, the facility and names (and village when supplied) must match.

`client_id` is a required client-generated UUID and is the report idempotency key. A new report returns `201`; resubmitting the same ID and content returns the existing report with `200`. Reusing the ID for different, otherwise-valid report content returns `409`. A malformed payload or mismatched patient identity/name returns `400`. Use the same ID and payload for network retries.

`age` is required (0–120 or `null`) and `gender` is required (`female`, `male`, `other`, or `unknown`); both are stored as snapshots for the encounter. `symptoms` is a required list of distinct values from `fever`, `cough`, `diarrhea`, `other` (an empty list is allowed). `action_taken` is optional, up to 2,000 characters. `occurred_at` is an optional ISO 8601 timestamp and cannot be more than 24 hours in the future; if omitted, the server uses the submission time.

Response fields: `id` (server report UUID), `client_id`, `patient` (patient UUID), `name`, `age`, `gender`, `symptoms`, `action_taken`, `occurred_at`, and `created_at` (server receipt time). `patient_name` is an optional write-only field; if sent, it must match the patient name.

List filters: `patient`, `patient__facility`. Search: patient first/last name and `action_taken`. Ordering: `created_at`, `patient__last_name`.

## Offline synchronization

### Submit a batch

`POST /api/v1/sync/batches/`

```json
{
  "client_batch_id":"dd35412a-28c8-4bea-9be2-b1b90414bfad",
  "reports":[
    {
      "client_id":"2bd4f2bd-b7a0-460c-9db0-e58108fb22e0",
      "patient":"bf9886a3-8d6a-49bb-b865-79013b7de4b9",
      "age":34,
      "gender":"female",
      "symptoms":["fever"],
      "action_taken":"Referred to health centre"
    }
  ]
}
```

`reports` must contain 1–100 report payloads in the same shape as the patient-report endpoint. A new batch returns `201`. Each item is processed independently; invalid items do not prevent valid items in the same batch from being saved.

Batch response fields: `id`, `client_batch_id`, `status` (`complete`, `partial`, `failed`), `item_count`, `success_count`, `rejected_count`, `received_at`, `completed_at`, and `items`. Each item includes its 1-based `position`, `client_id` (or `null` if invalid), `status` (`created`, `duplicate`, `rejected`, `conflict`), `report_id` (or `null`), and `errors`.

Keep `client_batch_id` stable for a retry and resend the exact same JSON payload. An identical retry returns the stored batch with `200`; reusing the batch ID with a different payload or account returns `409`.

### Get a batch result

`GET /api/v1/sync/batches/{client_batch_id}/`

The submitting user can retrieve their batch. Staff can retrieve any batch. Other users receive `404`.

## Reporting summary

`GET /api/v1/reports/summary/`

Query parameters:

| Parameter | Type | Behavior |
| --- | --- | --- |
| `start_date` | `YYYY-MM-DD` | Inclusive; defaults to 29 days before `end_date` |
| `end_date` | `YYYY-MM-DD` | Inclusive; defaults to today in Africa/Blantyre |
| `facility` | UUID | Optional facility filter |
| `symptom` | enum | Optional filter: `fever`, `cough`, `diarrhea`, `other` |

The date range must be ordered and no longer than 366 days. The response contains `start_date`, `end_date`, `symptom`, `total_reports`, `actions_recorded`, `symptom_counts`, `daily_counts`, and `facility_counts` (facility ID, name, district, report count). It contains aggregate data only, not patient records. Non-staff results are limited to active memberships. With a `symptom` filter, `total_reports` counts reports containing that symptom, while `symptom_counts` includes co-occurring symptoms. `daily_counts` includes dates with reports only.

## Audit events

Collection: `GET /api/v1/audit/events/`  
Detail: `GET /api/v1/audit/events/{id}/`

Staff-only, read-only endpoints. Results are paginated. Filters: `actor`, `action`, `resource_type`, `resource_id`. Search: resource ID and actor email. Ordering: `created_at`, `action`, `resource_type` (default newest first).

Fields: `id`, `actor` (current user UUID or `null`), `actor_id` (recorded actor UUID), `actor_email` (or `null`), `action`, `resource_type`, `resource_id`, `metadata`, and `created_at`. Audit metadata intentionally excludes patient names, symptoms, and action text.

## Common integration notes

- `PUT` replaces all writable fields; prefer `PATCH` for partial edits.
- UUIDs returned by the patient and report APIs should be stored by the client. New offline patients can use a client-generated UUID in the nested report identity.
- Patient, facility, organization, and report IDs are not interchangeable; `patient` in a report is a patient UUID, while `facility` is a facility UUID.
- Use `occurred_at` for the time the encounter happened. `created_at` / `received_at` are server-side timestamps.
- Do not retry a conflicting request with a new random ID automatically. Surface `409` to the client so the item can be reconciled rather than duplicated.

## Suggested client flow

1. Sign in with the administrator-issued email and password, then securely store the returned MoyoCare JWTs.
2. Create a patient profile online with `POST /patients/`, or create the patient and first report together using a client-generated patient UUID in `POST /patient-reports/`.
3. Store the returned patient and report IDs locally.
4. Queue reports while offline. Give each report and batch a stable client UUID.
5. Submit queued reports through `POST /sync/batches/`; retain the batch response and retry with the same batch ID and payload after a transport failure.
6. For `partial` or `failed` batches, inspect each item's `status` and `errors`; correct rejected items and submit a new batch ID. Keep the report `client_id` when retrying an item rejected before saving. For a `conflict`, reconcile the existing report ID before deciding whether a new report ID is appropriate.

## Error handling

| Status | Meaning | Client behavior |
| --- | --- | --- |
| `400` | Invalid fields, malformed UUID/date, or patient identity mismatch | Show field errors and correct the submitted data |
| `401` | Missing, expired, revoked, or invalid authentication | Obtain or refresh tokens; sign in again if refresh fails |
| `403` | Authenticated account lacks the required staff permission | Do not retry without an authorized account |
| `404` | Resource does not exist or is outside the caller's facility scope | Refresh local references; avoid revealing cross-facility IDs |
| `405` | Method is not supported for this route (for example deleting a patient/report) | Use the supported method; deactivate patient profiles with `PATCH` |
| `409` | An idempotency key was reused with different valid content, or deletion is blocked by dependents | Reconcile IDs/payloads or deactivate the dependent facility/organization |

Typical field validation body:

```json
{"gender":["\"unknown-value\" is not a valid choice."]}
```

Some conflicts use a `detail` field; report idempotency conflicts use a `client_id` field; sync item validation errors are returned inside that item's `errors` object.
