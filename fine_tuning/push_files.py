# Upload fine-tuning files
import os
from openai import AzureOpenAI

def push_files():
    client = AzureOpenAI(
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),
      api_version="2024-02-01"  # This API version or later is required to access fine-tuning for turbo/babbage-002/davinci-002
    )

    training_file_name = '../dataset/output_openai_train.jsonl'
    validation_file_name = '../dataset/output_openai_val.jsonl'

    # Upload the training and validation dataset files to Azure OpenAI with the SDK.
    if not os.path.exists(training_file_name):
        print("文件不存在：", training_file_name)
        return
    if not os.path.exists(validation_file_name):
        print("文件不存在：", validation_file_name)
        return

    training_response = client.files.create(
        file=open(training_file_name, "rb"), purpose="fine-tune"
    )
    training_file_id = training_response.id

    validation_response = client.files.create(
        file=open(validation_file_name, "rb"), purpose="fine-tune"
    )
    validation_file_id = validation_response.id

    print("Training file ID:", training_file_id)
    print("Validation file ID:", validation_file_id)

if __name__ == '__main__':
    push_files()
