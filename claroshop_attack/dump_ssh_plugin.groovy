def f = new File('/var/jenkins_home/jenkins.plugins.publish_over_ssh.BapSshPublisherPlugin.xml')
if (f.exists()) {
    println("FILE_EXISTS size=" + f.length())
    println("===XML_START===")
    println(f.text)
    println("===XML_END===")
} else {
    println("FILE_NOT_FOUND")
    // buscar alternativas
    def home = new File('/var/jenkins_home')
    home.eachFileMatch(~/.*publish_over_ssh.*/) { println("FOUND: " + it.absolutePath) }
}
