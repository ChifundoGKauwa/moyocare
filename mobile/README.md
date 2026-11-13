# MoyoCare Android app

The Android client is being built with Kotlin and Jetpack Compose. The supplied screen references are kept in `design/`.

## Current starting point

- Compose onboarding and administrator-issued email/password login.
- JWT login against `POST /api/v1/auth/token/`.
- Session tokens are encrypted with an Android Keystore key before local storage.
- Compose previews for the dashboard, patient directory, patient registration, field schedule, and sync screens.
- The preview screens use sample data. Patient persistence, facility selection, and synchronization are not connected yet.

## Open and run

Open the `mobile/` directory in Android Studio with JDK 17 and Android SDK 36 installed. The project uses Gradle 8.13 and Kotlin 2.2.20.

By default, the debug build targets Django on the Android emulator at `http://10.0.2.2:8123/api/v1/`. To point at a different development server, add this to `mobile/gradle.properties`:

```properties
MOYOCARE_API_BASE_URL=http://192.168.1.10:8123/api/v1/
```

Cleartext HTTP is enabled for debug builds to support local development and disabled for release builds. Release deployments must use an HTTPS API URL.
