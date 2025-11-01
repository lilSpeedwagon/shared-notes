import fastapi

app = fastapi.FastAPI(
	title='Shared Notes API',
	description='A simple notes sharing service',
	version='0.1.0',
)


@app.get('/')
async def hello_world():
	return {'message': 'Hello World'}

