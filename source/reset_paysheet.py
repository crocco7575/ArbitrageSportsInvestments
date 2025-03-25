import pandas as pd


columns = ["Account 1", "Account 2", "Amount"]

df = pd.DataFrame(columns=columns)

# Save the DataFrame as a CSV file
df.to_csv("./weeklypaysheet.csv", index=False)

print("CSV file created successfully")