import sys
with open('test_result.txt', 'w') as f:
    f.write('Starting test...\n')
    from main import app
    f.write('App imported\n')
    from fastapi.testclient import TestClient
    f.write('TestClient imported\n')
    client = TestClient(app)
    f.write('Client created\n')
    response = client.get('/health')
    f.write('Health: ' + str(response.status_code) + '\n')
    response = client.get('/')
    f.write('Root: ' + str(response.status_code) + '\n')