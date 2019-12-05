
DEVELOPMENT INSTRUCTIONS

The below assume a Mac
For couchbase:

Install homebrew if not present:
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
Then install libcouchbase
    brew install libcouchbase
Then pip install -r requirements.txt in your virtual environment

docker run -d --name db -p 8091-8096:8091-8096 -p 11210-11211:11210-11211 couchbase
Go to http://localhost:8091
Set up creds as Administrator and password
Create testbucket and then testuser and add access


Docker compose files can be found at https://github.com/simplesteph/kafka-stack-docker-compose/blob/master/zk-single-kafka-single.yml

Generating symmetric keys:
 from jwcrypto import jwk
>>> key = jwk.JWK.generate(kty='oct', size=256)
>>> key.export()

Generate asymmetric:
openssl req -newkey rsa:512 -nodes -keyout key.pem -x509 -days 1000 -out certificate.pem
Don't do 2048 or it'll be a huge token and slow