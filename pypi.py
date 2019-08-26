import shutil, os

# delete dist directory, if it exists
if os.path.exists("./dist"):
    if not os.path.isfile("./dist"):
        shutil.rmtree("./dist")

# store in format "username:password"
creds = os.environ["PYPI_CREDENTIALS"].split(":")
username = creds[0]
password = "".join(creds[1:])

# build and upload
os.system("python setup.py sdist bdist_wheel")
os.system(f"twine upload dist/* -u \"{username}\" -p \"{password}\"")
