import boto3
import os  # Pour manipuler les noms de fichiers


def lambda_handler(event, context):
    # Initialize clients for Polly and S3
    polly_client = boto3.client('polly')
    s3_client = boto3.client('s3')
    
    # Specify the S3 bucket name
    s3_bucket = 'myudemycourses'
    target_prefix = 'test/'  # Préfixe des fichiers source
    output_prefix = 'output_audio2/'  # Préfixe des fichiers générés
    
    try:
        # List all objects in the bucket
        objects = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=target_prefix)
        
        if 'Contents' not in objects:
            return {
                'statusCode': 200,
                'body': 'No files found in the bucket.'
            }

        # Process each object in the bucket
        for obj in objects['Contents']:
            s3_key = obj['Key']
            
            # Skip non-SSML or text files if necessary
            if not (s3_key.endswith('.ssml') or s3_key.endswith('.txt')):
                print(f"Skipping non-text file: {s3_key}")
                continue
            
            # Extract file name without extension
            file_name = os.path.basename(s3_key).rsplit('.', 1)[0]
            output_key = f"{output_prefix}{file_name}.mp3"  # Nom personnalisé
            
            # Read the content of the file
            text_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            text_content = text_object['Body'].read().decode('utf-8')
            
            # Synthesize speech and save it directly to the S3 bucket
            response = polly_client.start_speech_synthesis_task(
                Engine='long-form',  
                LanguageCode='en-US',
                OutputFormat='mp3',
                Text=text_content,
                VoiceId='Danielle',  # Change voice ID as needed
                TextType='ssml' if s3_key.endswith('.ssml') else 'text',
                OutputS3BucketName=s3_bucket,
                OutputS3KeyPrefix=output_key  # Nom du fichier généré
            )
            
            print(f"Speech synthesis task started for: {s3_key}")
            print(f"Generated file will be: {output_key}")
        
        return {
            'statusCode': 200,
            'body': 'Text-to-speech conversion tasks started for all applicable files.'
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"An error occurred: {e}"
        }

