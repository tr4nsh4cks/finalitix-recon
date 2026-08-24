def r = ["bash","-c","cat /var/jenkins_home/.bash_history 2>/dev/null | head -500"].execute().text
println r
