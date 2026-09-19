#!/usr/bin/env python3
"""Consolidate all HEXAGON GLM results into final JSON"""
import json

# Load original results
with open(r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_results.json', 'r', encoding='utf-8') as f:
    main = json.load(f)

# Load IntelX retry
with open(r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_intelx_retry.json', 'r', encoding='utf-8') as f:
    intelx = json.load(f)

# Load emails consolidated
with open(r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_emails_consolidated.json', 'r', encoding='utf-8') as f:
    emails = json.load(f)

# Replace vector_1_intelx error with actual data
main['vectors']['vector_1_intelx'] = {
    'data': {
        'phonebook': intelx.get('phonebook', {}),
        'intelligent': intelx.get('intelligent', {}),
        'file_reads': intelx.get('file_reads', []),
        'consolidated_emails': emails
    }
}

# Add summary section
main['summary'] = {
    'target': 'disperso.com',
    'parent_company': 'tuxpan.cl',
    'vps_used': '64.177.83.195',
    'agent': 'glm-5.2 (HEXAGON internal)',
    'key_findings': {
        'intelx_emails_real': emails.get('tuxpan_real_emails', []),
        'intelx_emails_disperso': emails.get('disperso_emails', []),
        'intelx_emails_inferred_disperso': emails.get('inferred_disperso_emails', []),
        'intelx_anonymized_count': len(emails.get('tuxpan_anon_emails', [])),
        'github_repos_target': 0,
        'github_commits_target': 0,
        'github_secrets': 0,
        'notification_endpoint_bypass': True,
        'notification_endpoint_200_gateway': True,
        'notification_endpoint_403_cdn': True,
        'jwt_null_alg_bypass': False,
        'actuator_exposed': False,
        'api_docs_exposed': False,
    },
    'vulnerabilities': {
        'V1_notification_unauth_gateway': {
            'severity': 'MEDIO',
            'description': 'POST /api/v1/notification en API Gateway directo acepta cualquier JSON sin auth (200 vacio). CloudFront bloquea pero bypass via rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod.',
            'impact': 'XSS stored / SSTI / webhook injection / lead injection si se renderiza en panel admin o envia emails internos',
            'evidence': '14 payloads XSS/SSTI/webhook todos 200 (0 bytes) en gateway, 403 en CDN'
        },
        'V2_api_gateway_direct_exposed': {
            'severity': 'BAJO',
            'description': 'API Gateway directo (rdrrxexkm4.execute-api.us-east-2.amazonaws.com/prod) accesible sin CloudFront',
            'impact': 'Bypass de WAF/rate limit de CloudFront'
        },
        'V3_user_enum_via_cognito': {
            'severity': 'BAJO',
            'description': 'ForgotPassword con PreventUserExistenceErrors parcial - mask a***@d*** filtra admin@disperso.com',
            'impact': 'Confirmacion de usuarios validos'
        }
    },
    'negative_results': {
        'jwt_null_alg': 'No funciona - Cognito valida RS256 correctamente (168 tests 401/403)',
        'actuator': 'No expuesto (92 tests 403/404)',
        'swagger_api_docs': 'No expuesto (403)',
        'github_code_search': 'Requiere auth (401) - sin token GitHub',
        'intelx_intelligent_leaks': '0 records - tier free no da acceso a leaks'
    },
    'next_steps': [
        'Probar spray contra soporte.disperso.com con 10 emails reales de tuxpan.cl + 20 inferred de disperso.com (sin captcha, sin rate limit)',
        'Verificar webhook.site 8d9e1f2a-3b4c-5d6e-7f8a-9b0c1d2e3f4a para callbacks XSS (panel admin)',
        'LinkedIn OSINT para empleados Disperso/Tuxpan - generar mas emails',
        'Probar Cognito SRP auth con 2Captcha si conseguimos email+password',
        'Subdomain brute force en *.dev.disperso.com, *.qa.disperso.com, *.shd.disperso.com'
    ]
}

# Save final
out = r'c:\xampp\htdocs\pentagi\disperso_recon\hexagon_glm_results.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(main, f, indent=2, default=str)
print(f'Saved final consolidated results to {out}')
print(f'File size: {len(json.dumps(main, default=str))} chars')

# Print summary
print('\n=== FINAL SUMMARY ===')
print(f'Vectors completed: {list(main["vectors"].keys())}')
print(f'Real Tuxpan emails: {len(main["summary"]["key_findings"]["intelx_emails_real"])}')
print(f'Disperso emails: {len(main["summary"]["key_findings"]["intelx_emails_disperso"])}')
print(f'Inferred Disperso emails: {len(main["summary"]["key_findings"]["intelx_emails_inferred_disperso"])}')
print(f'Anonymized emails: {main["summary"]["key_findings"]["intelx_anonymized_count"]}')
print(f'Notification bypass: {main["summary"]["key_findings"]["notification_endpoint_bypass"]}')
print(f'JWT null alg bypass: {main["summary"]["key_findings"]["jwt_null_alg_bypass"]}')
print(f'Actuator exposed: {main["summary"]["key_findings"]["actuator_exposed"]}')
