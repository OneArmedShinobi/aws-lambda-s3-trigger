import json
import boto3
import os

# crea i client SNS e S3
sns = boto3.client('sns')
s3 = boto3.client('s3')

# legge l'ARN del topic SNS dalle variabili d'ambiente
TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:REGIONE:ACCOUNT_ID:PortfolioNotifications')

def lambda_handler(event, context):
    try:
        # log dell’evento
        print("Evento ricevuto:", json.dumps(event))

        # --- ELABORAZIONE FILE S3 ---
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        # scarica il file (non necessariamente lo leggi tutto se è grosso)
        response = s3.get_object(Bucket=bucket, Key=key)
        file_content = response['Body'].read().decode('utf-8')  # se testo
        file_size = response['ContentLength']

        print(f"File ricevuto: {key} dal bucket: {bucket}, dimensione: {file_size} bytes")
        # puoi anche fare altre elaborazioni sul contenuto qui (es. estrarre dati)

        # pubblica il messaggio su SNS in caso di successo
        message = f"Lambda completata con successo! File {key} di {file_size} bytes elaborato."
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=message,
            Subject='Lambda Execution Success'
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f'File {key} elaborato con successo!')
        }

    except Exception as e:
        # pubblica su SNS in caso di errore
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=f"Lambda fallita: {str(e)}",
            Subject='Lambda Execution Failure'
        )
        # rilancia l’eccezione per il log CloudWatch
        raise