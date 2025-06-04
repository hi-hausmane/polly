import boto3
import os  # For handling file names


def lambda_handler(event, context):
    # Initialize clients for Polly and S3
    polly_client = boto3.client('polly')
    s3_client = boto3.client('s3')
    
    # TODO: Replace the following values with your actual S3 bucket and folder names
    s3_bucket = 'your-s3-bucket-name'            # e.g., 'my-audio-files-bucket'
    target_prefix = 'your/input/folder/'         # e.g., 'texts/' - folder with .txt or .ssml files
    output_prefix = 'your/output/folder/'        # e.g., 'audio/' - folder where MP3s will be saved

    try:
        # List all objects in the target prefix
        objects = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=target_prefix)
        
        if 'Contents' not in objects:
            return {
                'statusCode': 200,
                'body': 'No files found in the bucket.'
            }

        # Process each .txt or .ssml file
        for obj in objects['Contents']:
            s3_key = obj['Key']
            
            # Skip unsupported files
            if not (s3_key.endswith('.ssml') or s3_key.endswith('.txt')):
                print(f"Skipping non-text file: {s3_key}")
                continue
            
            # Create output filename (MP3)
            file_name = os.path.basename(s3_key).rsplit('.', 1)[0]
            output_key = f"{output_prefix}{file_name}.mp3"
            
            # Read input file content
            text_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            text_content = text_object['Body'].read().decode('utf-8')
            
            # Start Polly speech synthesis task
            response = polly_client.start_speech_synthesis_task(
                Engine='long-form',
                LanguageCode='en-US',
                OutputFormat='mp3',
                Text=text_content,
                VoiceId='Danielle',  # You can change this to another supported Polly voice
                TextType='ssml' if s3_key.endswith('.ssml') else 'text',
                OutputS3BucketName=s3_bucket,
                OutputS3KeyPrefix=output_key
            )
            
            print(f"Started synthesis for: {s3_key}")
            print(f"Output will be: {output_key}")
        
        return {
            'statusCode': 200,
            'body': 'Polly tasks started for all applicable files.'
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"An error occurred: {e}"
        }
