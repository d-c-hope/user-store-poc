from couchbase.bucket import Bucket
# cb = Bucket('couchbase:///protected', password='secret')
cb = Bucket('couchbase://localhost/testbucket', username='testuser', password='password')
cb.flush()