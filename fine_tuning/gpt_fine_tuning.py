# Upload fine-tuning files
import os
from openai import AzureOpenAI

def fine_tune():
    client = AzureOpenAI(
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),
      api_version="2024-02-01"  # This API version or later is required to access fine-tuning for turbo/babbage-002/davinci-002
    )
    training_file_id = "file-980425b1f7ef4404835b543e061d6e78"
    validation_file_id = "file-7155d0a5eab54c899613987d63c3f539"
    # training_file_id = "file-de2fa0ec318348e9a4013458d74bff9e"
    # validation_file_id = "file-918934cf140a45ef9b0a6cf8581c6ed6"
    # training_file_id = "file-4e8667d8a8684a4c9d75aceea3795675"
    # validation_file_id = "file-82eebb1a690d412897b58796b28bdac8"

    response = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        validation_file=validation_file_id,
        model="gpt-35-turbo-0125", # Enter base model name. Note that in Azure OpenAI the model name contains dashes and cannot contain dot/period characters.
        hyperparameters={
            "n_epochs":2
        }
    )

    job_id = response.id

    # You can use the job ID to monitor the status of the fine-tuning job.
    # The fine-tuning job will take some time to start and complete.

    print("Job ID:", response.id)
    print("Status:", response.id)
    print(response.model_dump_json(indent=2))

if __name__ == '__main__':
    fine_tune()
