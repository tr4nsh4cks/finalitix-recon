"""Batch-hunt multiple images; save each output; print condensed highlights."""
import sys, os, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from image_hunt import hunt

IMAGES = [
    "docker-registry.nexus.dev.claroshop.com/ubi7-php72-fpm-ngx:latest",
    "docker-registry.nexus.dev.claroshop.com/ubi7-php72:latest",
    "docker-registry.nexus.dev.claroshop.com/docker-docker-jnlp-slave-msa-cs:latest",
    "docker-registry.nexus.dev.claroshop.com/docker-jnlp-slave-msa-cs:latest",
    "docker-registry.nexus.dev.claroshop.com/atomic-rhel7-jenkins-slave-maven-openjdk8:latest",
    "docker-registry.nexus.dev.claroshop.com/atomic-rhel7-jenkins-slave-maven-openjdk11:latest",
    "docker-registry.nexus.dev.claroshop.com/docker-jnlp-slave-php71-src-sonar:latest",
    "docker-registry.nexus.dev.claroshop.com/docker-jnlp-slave-php70-src-sonar-ii-modca1:latest",
    "docker-registry.nexus.dev.claroshop.com/docker-jnlp-slave-php54-src-sonar:latest",
    "docker-registry.nexus.dev.claroshop.com/docker-rh7-lnx-jnlp-slave:latest",
    "docker-registry.nexus.dev.claroshop.com/openjdk-jre11-jar-run:latest",
    "docker-registry.nexus.dev.claroshop.com/oracle-jre8-jar-run:latest",
    "docker-registry.nexus.dev.claroshop.com/atomic-rhel7-nginx-php-fpm72-gs:latest",
    "docker-registry.nexus.dev.claroshop.com/atomic-rhel7-nginx-php-fpm70:latest",
    "docker-registry.nexus.dev.claroshop.com/docker-jnlp-slave-php70-src-sonar-ii:latest",
    "docker-source-registry.amxdigital.net/docker-jnlp-slave-php72-src-sonar-iii:latest",
    "docker-source-registry.amxdigital.net/rh7-jenkins-slave-docker-node12:latest",
    "docker-source-registry.amxdigital.net/ubi7-php72-fpm-ngx:GA-1.1.1",
    "docker-source-registry.amxdigital.net/openjdk-jre11-jar-run:latest",
    "docker-source-registry.amxdigital.net/openjdk-jre8-jar-run:latest",
    "docker-source-registry.amxdigital.net/ol8-jre-17:17.0.6.0.10-3-1.0.4",
    "dockeregistry.amovildigitalops.com/docker-docker-jnlp-slave-msa-cs:latest",
]

INTERESTING = re.compile(
    r"(password|passwd|secret|api[_-]?key|private key|BEGIN.*PRIVATE|Nic3|DB_|NEXUS|nexus|"
    r"env-generator|settings\.xml|\.docker/config|id_rsa|\.pem|token)",
    re.I,
)


def short_name(img):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", img.split("/")[-1])


for img in IMAGES:
    out = os.path.join(HERE, f"hunt_{short_name(img)}.txt")
    if os.path.exists(out):
        print(f"[SKIP] {img} (already hunted)")
        continue
    print(f"\n########## {img}")
    try:
        text = hunt(img, out)
    except Exception as e:
        print(f"[ERR] {e}")
        continue
    # print only interesting lines with context
    lines = text.splitlines()
    hits = []
    for idx, line in enumerate(lines):
        clean = re.sub(r"^[\x00-\x08]+", "", line)
        if INTERESTING.search(clean) and "pear" not in clean.lower() and "doc/" not in clean:
            hits.append(clean.strip())
    if hits:
        for h in hits[:40]:
            print("  HIT:", h[:200])
    else:
        print("  (no interesting hits)")

print("\nBATCH DONE")
