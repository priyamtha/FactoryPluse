\# Python Workflow



\## How to Execute



Run:



```bash

python scripts/data\_workflow.py

```



\## Functions



\### ingest\_data(filepath)



Reads data from a CSV file and returns a Pandas DataFrame.



\### process\_data(df)



Removes duplicate rows and fills missing numeric values.



\### output\_results(df, output\_path)



Saves the processed data to a CSV file and prints a success message.



\## Using Another Dataset



Replace:



data/raw/sample.csv



with the path to your own CSV file.

