# ResidentsGroupingApp

This web application, built using FastAPI, is designed to group individuals based on identical addresses. The application is developed in two separate branches, offering two different solutions to the task:

- main: Implements the address grouping using the Jaccard algorithm.
- v2: Provides an alternative approach utilizing the FuzzyWuzzy library, which is based on Levenshtein Distance to calculate the differences between sequences.

Users can input data either through a user interface (UI) for manual text entry or by uploading a .csv file. The results are displayed within the UI and provide an option for users to download the results as a .txt file.

## Getting set up
1. Ensure Python 3.x is installed.
2. Create venv
3. Install necessary libraries using pip install -r requirements.txt.
4. Run the app: ```uvicorn main:app --host 0.0.0.0 --port 8000```
5. Access the web application in a browser at http://localhost:8000

## Input Options
- File Upload: Users can upload a UTF-8 encoded .csv file containing two columns: Name and Address.
- Text Input: Direct text input is available on the UI for manual entry. Each pair of name and address should be on a new line.

## Output
- Text Document: The output file presents each line as a comma-separated list of names belonging to individuals living at the same address. Names on each line are sorted alphabetically. Additionally, the lines within the file are sorted alphabetically.
- UI Visualization: The results are visualized within the web interface.

#### Example Input
```
Ivan Draganov,"ul. Shipka 34, 1000 Sofia, Bulgaria"
Leon Wu,"1 Guanghua Road, Beijing, China 100020"
Ilona Ilieva,"ул. Шипка 34, София, България"
Dragan Doichinov,"Shipka Street 34, Sofia, Bulgaria"
Li Deng,"1 Guanghua Road, Chaoyang District, Beijing, P.R.C 100020"
Frieda Müller,"Konrad-Adenauer-Straße 7, 60313 Frankfurt am Main, Germany"
```

#### Expected output
```
Dragan Doichinov, Ilona Ilieva, Ivan Draganov
Frieda Müller
Leon Wu, Li Deng
```
