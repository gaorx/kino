
def main(k):
    k.write('package.json', content=k.to_json({
        'name': '{{name}}'
    }, pretty=True), args={'name': 'NAME111'})
    k.copy('README.md')
    k.copy('README1.md', 'README.md')
    k.write('python.ignore', content=k.curl('https://raw.githubusercontent.com/github/gitignore/master/Python.gitignore'))
    k.mkdir_p('src/main/java')
    k.write('src/main/kotlin/App.kt', content='kt11')