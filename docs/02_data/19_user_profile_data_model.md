# User Profile Data Model

## Objetivo
Permitir recomendaciones muy precisas sin mezclar identidad, economía, salud/necesidades sensibles y telemetría.

## Separación lógica

### `user_identity`
- user_id
- auth_provider
- email/identifier
- account_created_at
- consent versions

### `residential_profile`
- profile_id
- user_id reference
- household structure
- tenure preference
- housing requirements
- mobility preferences
- priority configuration

### `financial_profile`
Zona protegida:
- exact_net_income
- exact_savings
- exact_monthly_debt
- income_stability

Derivados:
- income_band
- savings_band
- debt_ratio_band
- affordability_band

### `location_anchor`
- type: work/family/campus/other
- encrypted_exact_coordinate optional
- analysis_coordinate
- precision_level
- typical_days
- schedule

### `sensitive_needs`
Separado:
- mobility_accessibility_required
- dependency_related_needs
- other explicit accessibility flags

Solo con consentimiento explícito cuando aplique.

### `analytics_profile`
No contiene PII directa:
- household_segment
- affordability_segment
- preference clusters
- aggregated behavior labels

## Regla
PRO nunca consulta `financial_profile` o `sensitive_needs` de un individuo.

Solo servicios autorizados del dominio PUBLIC pueden usar datos exactos para recomendaciones del propio usuario.
