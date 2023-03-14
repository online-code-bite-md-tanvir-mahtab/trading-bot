import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]}, index=['a', 'b', 'c'])

# Get the index of the DataFrame
index = df.set_index(df.index)

# Print the index
print(index)
print(df)