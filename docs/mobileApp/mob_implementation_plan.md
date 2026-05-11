# [Mobile App Implementation Plan: x_mobile_app]

This plan outlines the steps to build the `x_mobile_app` Flutter application, following the designs and requirements specified in [docs/mobileApp.md](file:///Users/mpamdev03/projects/python/xInvest/docs/mobileApp.md) and the Stitch project `448710195442555199`.

## User Review Required

> [!IMPORTANT]
> The app will be built using **Flutter (Dart)**. I will use the **Stitch Build Loop** skill, adapted for mobile development, to iteratively generate and integrate screens.

## Proposed Changes

### [Flutter Project Structure]
- **Root**: `x_mobile_app/`
- **Stitch Config**: `x_mobile_app/.stitch/` — stores project metadata, design tokens, and the build loop baton.
- **Source Code**: `x_mobile_app/lib/` — standard Flutter directory for widgets, models, and services.

### [Build Loop Setup]
1.  **DESIGN.md**: Synthesize the "Financial Atelier" design system from the Stitch project.
2.  **SITE.md**: Define the sitemap (Login, OTP, Portfolio) and roadmap.
3.  **next-prompt.md**: Initialize the first baton (Login screen).

### [Screen Generation & Integration]
- Use `generate_screen_from_text` to create high-fidelity designs.
- Manually translate Stitch HTML/CSS to Flutter widgets (or use AI assistance) to ensure pixel-perfect implementation.
- Integrate backend APIs:
    - **Login**: `POST http://localhost:8000/api/v1/auth/login/`
    - **OTP**: `POST http://localhost:8000/api/v1/auth/verify-otp/`
    - **Portfolio**: `GET http://localhost:8080/api/v1/invesInfo`

## Verification Plan

### Automated Tests
- `flutter test` for unit and widget tests.
- Verify API connectivity using local dev servers.

### Manual Verification
- Visual comparison between Stitch screenshots and the running Flutter app.
- End-to-end flow from Login to Portfolio.
