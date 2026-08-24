"""Build final deliverables: nexus_images.json + CREDENTIALS_EXTRACTED.md + pivot route."""
import json, os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

# 1. Consolidated image list
local_tags = json.load(open(os.path.join(HERE, "docker_local_tags.json"), encoding="utf-8"))
local_tags = [t for t in local_tags if "<none>" not in t]

jenkins_refs = [
    "cs-docker-registry.nexus.dev.claroshop.com/sears/beta-mesa-regalos-java-api",
    "cs-docker-registry.nexus.dev.claroshop.com/sears/contador-java-api",
    "cs-docker-registry.nexus.dev.claroshop.com/sears/mesa-regalos-java-api",
    "docker-registry.nexus.dev.claroshop.com/atomic-rhel7-nginx-php-fpm72-gs",
    "docker-registry.nexus.dev.claroshop.com/openjdk-jre11-jar-run",
    "docker-registry.nexus.dev.claroshop.com/oracle-jre8-jar-run",
    "dockeregistry.amovildigitalops.com/atomic-rhel7-php-fpm70",
]

catalog = {
    "nexus_registry": "docker-registry.nexus.dev.claroshop.com",
    "nexus_status": "FIREWALLED - 172.27.141.25 unreachable from Jenkins master (container) and docker host 172.27.140.148; external nginx (200.57.183.182) only exposes 80/443 and does not route /v2/ (404). Catalog reconstructed from local docker host images + Jenkins job configs + GitLab repos.",
    "nexus_credentials": {"user": "jenkins-ng.dev.claroshop.com", "pass": "dtvV50vwfGq5CO9", "source": "Jenkins credentials.xml (id=nexus)"},
    "docker_host": "172.27.140.148:4243 (no auth, Docker 1.13.1 API 1.26)",
    "images_on_docker_host": sorted(local_tags),
    "image_refs_from_jenkins_jobs": sorted(set(jenkins_refs)),
    "registries_seen": [
        "docker-registry.nexus.dev.claroshop.com",
        "cs-docker-registry.nexus.dev.claroshop.com",
        "docker-source-registry.amxdigital.net",
        "dockeregistry.amovildigitalops.com",
    ],
    "images_with_db_tools": {
        "ubi7-php72 (pivot04 running)": "PHP mysqli, pdo_mysql, mongodb, pdo_sqlite (NO mysql CLI)",
        "docker-jnlp-slave-php72-src-sonar-ii": "IBM DB2 client (/opt/ibm/db2/V10.5) + PHP",
        "rh7-jenkins-slave-docker-php72-sonar": "PHP + env-generator.sh (SECRETS)",
    },
    "image_secrets_found": {
        "rh7-jenkins-slave-docker-php72-sonar": "/opt/env-generator/env-generator.sh -> 7 Laravel .envs base64 (ares, medusa, triton, apolo, busiris, ciclope, atenea) DB pass Nic3.P4ssw0rd (mavericksgateway.net DEV)",
    },
    "total_local_images": 30,
}

with open(os.path.join(HERE, "nexus_images.json"), "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=1, ensure_ascii=False)
print("nexus_images.json written:", len(local_tags), "local tags +", len(jenkins_refs), "jenkins refs")
