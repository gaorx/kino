# ABC

README = "# {{target_name}}\n"

BUILD_GRADLE = """
plugins {
  id 'org.springframework.boot' version '2.4.4'
  id 'io.spring.dependency-management' version '1.0.11.RELEASE'
  id 'java'
}
group = '{{group}}'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '1.8'
repositories {
  maven{ url 'http://maven.aliyun.com/nexus/content/groups/public/' }
  mavenCentral()
}
dependencies {
  implementation 'org.springframework.boot:spring-boot-starter-web'
  testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
test {
  useJUnitPlatform()
}
"""

APP_JAVA = """
package {{package}};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
"""

HELLO_CONTROLLER_JAVA = """
package {{package}}.controller;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;

@RestController
public class HelloController {
    @RequestMapping("/")
    public String index() {
        return "Greetings from Spring Boot!";
    }
}
"""


def main(k):
    args = k.get_args([
        k.option('--group', required=True, help="project group"),
        k.option('--artifact', required=True, help="project artifact"),
        k.option('--name', default=k.target_name, help="project name"),
        k.option('--package', default='', help="com.group.artifact"),
    ])
    if not args.package:
        args.package = f"{args.group}.{args.artifact}"
    args.package_dirname = args.package.replace('.', '/')
    k.write('README.md', README, args=args)
    k.write('build.gradle', BUILD_GRADLE, args=args)
    k.write('.gitignore', k.curl_gitignore('Java'))
    k.write('src/main/resources/application.properties', '')
    k.mkdir('src/main/resources/static')
    k.mkdir('src/main/resources/templates')
    k.write(f"src/main/java/{args.package_dirname}/App.java", APP_JAVA, args=args)
    k.write(f"src/main/java/{args.package_dirname}/controller/HelloController.java",
            HELLO_CONTROLLER_JAVA, args=args)
    k.mkdir(f"src/main/java/{args.package_dirname}/service")
    k.mkdir(f"src/main/java/{args.package_dirname}/repository")
    k.mkdir(f"src/main/java/{args.package_dirname}/util")
    k.log("Start server: '[bold purple u]gradle bootRun[/bold purple u]'")
