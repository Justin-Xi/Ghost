import os
from openai import AzureOpenAI

if __name__ == '__main__':
    client = AzureOpenAI(
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),
      api_version="2024-02-01"  # This API version or later is required to access fine-tuning for turbo/babbage-002/davinci-002
    )
    # job_id = "ftjob-bd5d3b1f014c48bf911c86ff48867a7b"
    # job_id = "ftjob-000b85287a9e4653b41cf3bbb8d6183c"
    job_id = "ftjob-0e7fd4844e444516b60a733c3bfa8ca7"

    response = client.fine_tuning.jobs.retrieve(job_id)

    print("Job ID:", response.id)
    print("Status:", response.status)
    print(response.model_dump_json(indent=2))
