import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
	"""Shows basic usage of the Drive Labels API.

		Prints the first page of the customer's Labels.
	"""
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json',
																											SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())
	try:
		service = build('drive', 'v3', credentials=creds)
		response = service.files().list(pageSize=10, fields="files(id, name)").execute()
		files = response.get("files", [])

		if not files:
			print("No se encontraron archivos.")
		else:
			print("Archivos en tu Google Drive:")
			for file in files:
					print(f"{file['name']} ({file['id']})")
	except HttpError as error:
		# TODO (developer) - Handle errors from Labels API.
		print(f'An error occurred: {error}')

if __name__ == '__main__':
  main()