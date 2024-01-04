mkdir package
cd package
pip install --target . requests boto3 "git+https://github.com/hamukazu/tiny_bsky"
zip -r ../package.zip *
cd ..
zip -r package.zip bot.py lambda_function.py prime.py bsky.ini aws_credentials
