# NoteTakerAI
Automatic note taking app, built with OpenAI's GPT 4o as backend

## Usage

- ### API-Key
    - Add a .env file to your project root
    - Add your OpenAI API key in the format: 

    ```
    OPENAI_API_KEY = "<API_KEY>"
    ```
    ( Your api key need to have access to model  gpt-4o-2024-05-13. or higher)

- ### Install Dependencies
    - Ensure you have Anaconda/ Miniconda installed 
    ( https://docs.anaconda.com/anaconda/install/ )
    - Run the following to make a conda environment with all dependecies

    ```
    conda env create -f dependencies.yml
    conda activate cuda-env
    ```

- ### Start 
    - Run app
    ```
    python main.py
    ```
