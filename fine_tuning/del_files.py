import os
from openai import AzureOpenAI

if __name__ == '__main__':
    os.environ['AZURE_OPENAI_API_KEY'] = "a7d194b6355e4b5b83a47979fe20d245"
    os.environ['AZURE_OPENAI_ENDPOINT'] = "https://loox-eastus2.openai.azure.com/"

    delete_now = True

    client = AzureOpenAI(
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_key=os.getenv("AZURE_OPENAI_API_KEY"),
      api_version="2024-02-01"  # This API version or later is required to access fine-tuning for turbo/babbage-002/davinci-002
    )
    print('Checking for existing uploaded files.')
    results = []

    # Get the complete list of uploaded files in our subscription.
    files = client.files.list().data
    print(f'Found {len(files)} total uploaded files in the subscription.')

    # Enumerate all uploaded files, extracting the file IDs for the
    # files with file names that match your training dataset file and
    # validation dataset file names.
    for item in files:
        if item.filename.endswith("output_openai_train_022_01_02_0102_cmn_with_cot_6000.jsonl"):
            print("Del file:", item.filename)
            results.append(item.id)
    print(f'Found {len(results)} already uploaded files that match our files')

    if delete_now:
        # Enumerate the file IDs for our files and delete each file.
        print(f'Deleting already uploaded files.')
        for id in results:
            client.files.delete(id)

    print("finsh")