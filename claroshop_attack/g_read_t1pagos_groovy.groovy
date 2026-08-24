// Lee los Groovy scripts de los jobs t1pagos y t1envios directamente del workspace
// Busca conexiones DB, environment vars, secretos

import jenkins.model.Jenkins

println "=== T1PAGOS / T1ENVIOS GROOVY SCRIPTS ==="

def TARGET_JOBS = [
    "cs_new_front/cs_new_pipe_build_t1pagos-api",
    "cs_new_front/cs_new_pipe_build_t1pagos-api-config",
    "se_new_front/se_new_pipe_build_t1pagos-api",
    "se_new_front/se_new_pipe_build_t1pagos-api-config",
    "sn_new_front/sn_new_pipe_build_t1pagos-api",
    "sn_new_front/sn_new_pipe_build_t1pagos-api-config",
    "pc_legacy_back/pc_legacy_pipe_build_pc-plataforma-claro",
    "t1e_new_back/t1e_new_back_crones/t1e_new_pipe_build_contadores-reps-admin-cron",
    "t1e_new_back/t1e_new_pipe_build_fullfilment-admin-api",
    "t1e_new_back/t1e_new_pipe_build_t1mw-bussiness-admin-api"
]

TARGET_JOBS.each { jobName ->
    def configPath = "/var/jenkins_home/jobs/" + jobName.replace("/", "/jobs/") + "/config.xml"
    def f = new File(configPath)
    if (!f.exists()) {
        println "NOT FOUND: ${jobName}"
        return
    }
    
    println "\n" + "=" * 70
    println "JOB: ${jobName}"
    println "=" * 70
    
    def content = f.text
    println content
    
    // Also check workspace
    def wsPath = "/var/jenkins_home/workspace/${jobName.split('/').last()}"
    def ws = new File(wsPath)
    if (ws.exists()) {
        println "\n--- WORKSPACE: ${wsPath} ---"
        ws.listFiles()?.each { println "  ${it.name}" }
    }
}

println "\n=== SEARCHING ALL JOBS FOR DB VARS ==="
Jenkins.getInstance().getAllItems().each { job ->
    def configPath = "/var/jenkins_home/jobs/" + job.fullName.replace("/", "/jobs/") + "/config.xml"
    def f = new File(configPath)
    if (!f.exists()) return
    
    def content = f.text
    // Look for direct DB connection strings
    if (content.contains("172.27.141.24") || content.contains("dbasears") || 
        content.contains("172.27.141.4:") || content.contains("3308") ||
        content.contains("3310") || content.contains("DB_HOST") ||
        content.contains("MYSQL_HOST") || content.contains("DATABASE_HOST")) {
        
        println "\nJOB WITH DB VARS: ${job.fullName}"
        content.split("\n").each { line ->
            if (line.contains("172.27.141.24") || line.contains("dbasears") ||
                line.contains("172.27.141.4:") || line.contains("3308") ||
                line.contains("3310") || line.toLowerCase().contains("db_host") ||
                line.toLowerCase().contains("mysql_host") || 
                line.toLowerCase().contains("database_host") ||
                (line.toLowerCase().contains("db_pass") && line.length() < 300)) {
                println "  LINE: ${line.trim().take(300)}"
            }
        }
    }
}
